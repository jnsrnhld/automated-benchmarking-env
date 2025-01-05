import numpy as np
from typing import Tuple
from collections import defaultdict
from bson.objectid import ObjectId

from .config import Config
from .ernest import Ernest
from .bell import Bell

relative_slack_up = 1.05
absolute_slack_up = 0
relative_slack_down = 0.85
absolute_slack_down = 0


def compute_predictions(
        scale_outs: np.ndarray, runtimes: np.ndarray, predicted_scale_outs: np.ndarray
) -> np.ndarray:
    """
    Computes predicted runtimes using interpolation and extrapolation models.

    Args:
        scale_outs (np.ndarray): Array of observed scale-outs.
        runtimes (np.ndarray): Array of observed runtimes corresponding to the scale-outs.
        predicted_scale_outs (np.ndarray): Array of scale-outs to predict runtimes for.

    Returns:
        np.ndarray: Array of predicted runtimes.
    """
    x = scale_outs.astype(float)
    y = runtimes.astype(float)
    x_predict = predicted_scale_outs.astype(float)

    # Determine interpolation and extrapolation ranges
    interpolation_mask = (x_predict >= x.min()) & (x_predict <= x.max())
    x_predict_interpolation = x_predict[interpolation_mask]
    x_predict_extrapolation = x_predict[~interpolation_mask]

    # Initialize predictions
    y_predict = np.zeros_like(x_predict)

    # Fit the Ernest model
    ernest = Ernest()
    ernest.fit(x, y)

    unique_scale_outs = np.unique(x).size

    if unique_scale_outs <= 2:
        # If very few data points, use the mean runtime
        y_predict[:] = y.mean()
    elif unique_scale_outs <= 5:
        # If too few data points, use the Ernest model
        y_predict[:] = ernest.predict(x_predict)
    else:
        # Use the Bell model for interpolation and Ernest for extrapolation
        try:
            bell = Bell()
            bell.fit(x, y)
            y_predict[interpolation_mask] = bell.predict(x_predict_interpolation)
            y_predict[~interpolation_mask] = ernest.predict(x_predict_extrapolation)
        except Exception as e:
            print(f"Bell failed: {e}")
            y_predict[:] = ernest.predict(x_predict)

    return y_predict.astype(int)


class EllisUtils:
    def __init__(self, db):
        """
        Initializes the EllisUtils class with a MongoDB database connection.

        Args:
            db: The MongoDB database object.
        """
        self.db = db

    def compute_initial_scale_out(
            self,
            app_event_id: str,
            app_signature: str,
            min_executors: int,
            max_executors: int,
            target_runtime_ms: int
    ) -> int:
        """
        Computes the initial scale-out value based on previous runs and predictions.

        Args:
            app_event_id (str): The current application event ID.
            app_signature (str): The application signature.
            min_executors (int): The minimum number of executors.
            max_executors (int): The maximum number of executors.
            target_runtime_ms (int): The target runtime in milliseconds.

        Returns:
            int: The computed initial scale-out value.
        """
        scale_outs, runtimes = self.get_non_adaptive_runs(app_event_id, app_signature)

        half_executors = (min_executors + max_executors) // 2

        if len(scale_outs) == 0:
            return max_executors
        elif len(scale_outs) == 1:
            return half_executors
        elif len(scale_outs) == 2:
            if max(runtimes) < target_runtime_ms:
                return (min_executors + half_executors) // 2
            else:
                return (half_executors + max_executors) // 2
        else:
            predicted_scale_outs = np.arange(min_executors, max_executors + 1)
            predicted_runtimes = self.compute_predictions_from_stage_runtimes(
                app_event_id, app_signature, predicted_scale_outs
            )

            # Filter candidate scale-outs where predicted runtime is less than the target
            candidate_scale_outs = predicted_scale_outs[predicted_runtimes < target_runtime_ms]

            if len(candidate_scale_outs) == 0:
                # Return the scale-out with the minimal predicted runtime
                return int(predicted_scale_outs[np.argmin(predicted_runtimes)])
            else:
                return int(candidate_scale_outs.min())

    def get_non_adaptive_runs(
            self, app_event_id: str, app_signature: str
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Retrieves non-adaptive runs prior to the given application event ID.

        Args:
            app_event_id (str): The current application event ID.
            app_signature (str): The application signature.

        Returns:
            Tuple[np.ndarray, np.ndarray]: Arrays of scale-outs and runtimes.
        """
        app_event_collection = self.db[Config.ELLIS_APP_EVENT_COLLECTION]

        pipeline = [
            {
                '$match': {
                    'app_id': app_signature,
                    '_id': {'$lt': ObjectId(app_event_id)}
                }
            },
            {
                '$lookup': {
                    'from': Config.ELLIS_JOB_EVENT_COLLECTION,
                    'let': {'appId': '$_id'},
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': [
                                        '$app_event_id',
                                        {'$toString': '$$appId'}
                                    ]
                                }
                            }
                        }
                    ],
                    'as': 'job_events'
                }
            },
            {
                '$unwind': '$job_events'
            },
            {
                '$project': {
                    'started_at': 1,
                    'scale_out': '$job_events.scale_out',
                    'duration_ms': '$job_events.duration_ms'
                }
            }
        ]

        result = list(app_event_collection.aggregate(pipeline))

        # Group by 'started_at'
        grouped = defaultdict(list)
        for doc in result:
            started_at = doc['started_at']
            scale_out = doc['scale_out']
            duration_ms = doc['duration_ms']
            grouped[started_at].append((scale_out, duration_ms))

        scale_outs_list = []
        runtimes_list = []

        for job_stages in grouped.values():
            scale_outs = [scale_out for scale_out, _ in job_stages]
            scale_out = scale_outs[0]
            non_adaptive = all(s == scale_out for s in scale_outs)
            if non_adaptive:
                runtime = sum(duration_ms for _, duration_ms in job_stages)
                scale_outs_list.append(scale_out)
                runtimes_list.append(runtime)

        scale_outs = np.array(scale_outs_list)
        runtimes = np.array(runtimes_list)

        return scale_outs, runtimes

    def compute_predictions_from_stage_runtimes(
            self, app_event_id: str, app_signature: str, predicted_scale_outs: np.ndarray
    ) -> np.ndarray:
        """
        Computes predicted runtimes for a range of scale-outs based on historical data.

        Args:
            app_event_id (str): The current application event ID.
            app_signature (str): The application signature.
            predicted_scale_outs (np.ndarray): Array of scale-outs to predict runtimes for.

        Returns:
            np.ndarray: Array of predicted runtimes corresponding to the predicted scale-outs.
        """
        job_runtime_data = self.gather_job_runtime_data(app_event_id, app_signature)

        predicted_runtimes_list = []

        for job_id in sorted(job_runtime_data.keys()):
            x_y_tuples = job_runtime_data[job_id]
            x = np.array([t[0] for t in x_y_tuples])
            y = np.array([t[1] for t in x_y_tuples])
            predicted_runtimes = compute_predictions(x, y, predicted_scale_outs)
            predicted_runtimes_list.append(predicted_runtimes)

        # Sum up the predicted runtimes across all jobs
        total_predicted_runtimes = np.sum(predicted_runtimes_list, axis=0)
        return total_predicted_runtimes

    def update_scaleout(self, app_event_id: str, job_id: int, job_end_time: int, current_scale_out: int) -> int:

        app_event = self.db[Config.ELLIS_APP_EVENT_COLLECTION].find_one({'_id': ObjectId(app_event_id)})
        app_signature = app_event['app_id']
        app_start_time = app_event['started_at']
        target_runtime = app_event['target_runtime']
        min_executors = app_event['min_executors']
        max_executors = app_event['max_executors']

        job_runtime_data = self.gather_job_runtime_data(app_event_id, app_signature)
        predicted_scale_outs = np.arange(min_executors, max_executors + 1)

        remaining_runtimes = []
        future_job_ids = sorted(k for k in job_runtime_data.keys() if k > job_id)
        for future_job_id in future_job_ids:
            x_y_tuples = job_runtime_data[future_job_id]
            x = np.array([t[0] for t in x_y_tuples])
            y = np.array([t[1] for t in x_y_tuples])
            predicted_runtimes = compute_predictions(x, y, predicted_scale_outs)
            remaining_runtimes.append(predicted_runtimes)

        if len(remaining_runtimes) <= 1:
            return -1

        next_job_runtimes = remaining_runtimes[0]
        future_jobs_runtimes = np.sum(remaining_runtimes[1:], axis=0)

        current_runtime = job_end_time - app_start_time
        next_job_runtime = next_job_runtimes[current_scale_out - min_executors]
        remaining_target_runtime = target_runtime - current_runtime - next_job_runtime
        remaining_runtime_prediction = future_jobs_runtimes[current_scale_out - min_executors]

        print(f"Current runtime: {current_runtime}")
        print(f"Next job runtime: {next_job_runtime}")
        print(f"Remaining target runtime: {remaining_target_runtime}")
        print(f"Remaining runtime prediction: {remaining_runtime_prediction}")

        if remaining_runtime_prediction > remaining_target_runtime * relative_slack_up + absolute_slack_up:
            candidate_scale_outs = np.where(future_jobs_runtimes < remaining_target_runtime * 0.9)[0]
            if len(candidate_scale_outs) > 0:
                next_scale_out_index = candidate_scale_outs[0]
            else:
                next_scale_out_index = np.argmin(future_jobs_runtimes)
            next_scale_out = predicted_scale_outs[next_scale_out_index]
            if next_scale_out != current_scale_out:
                return int(next_scale_out)

        elif remaining_runtime_prediction < remaining_target_runtime * relative_slack_down - absolute_slack_down:
            candidate_scale_outs = np.where(future_jobs_runtimes < remaining_target_runtime * 0.9)[0]
            if len(candidate_scale_outs) > 0:
                next_scale_out_index = candidate_scale_outs[0]
            else:
                next_scale_out_index = np.argmin(future_jobs_runtimes)
            next_scale_out = predicted_scale_outs[next_scale_out_index]
            if next_scale_out < current_scale_out:
                return int(next_scale_out)

        return current_scale_out

    def gather_job_runtime_data(self, app_event_id, app_signature):
        app_event_collection = self.db[Config.ELLIS_APP_EVENT_COLLECTION]
        pipeline = [
            {
                '$match': {
                    'app_id': app_signature,
                    '_id': {'$lt': ObjectId(app_event_id)}
                }
            },
            {
                '$lookup': {
                    'from': Config.ELLIS_JOB_EVENT_COLLECTION,
                    'let': {'appId': '$_id'},
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': [
                                        '$app_event_id',
                                        {'$toString': '$$appId'}
                                    ]
                                }
                            }
                        }
                    ],
                    'as': 'job_events'
                }
            },
            {
                '$unwind': '$job_events'
            },
            {
                '$project': {
                    'job_id': '$job_events.job_id',
                    'scale_out': '$job_events.scale_out',
                    'duration_ms': '$job_events.duration_ms'
                }
            },
            {
                '$sort': {'job_id': 1}
            }
        ]
        result = list(app_event_collection.aggregate(pipeline))

        # Group by 'job_id'
        job_runtime_data = defaultdict(list)
        for doc in result:
            job_id = doc['job_id']
            scale_out = doc['scale_out']
            duration_ms = doc['duration_ms']
            job_runtime_data[job_id].append((scale_out, duration_ms))
        return job_runtime_data
