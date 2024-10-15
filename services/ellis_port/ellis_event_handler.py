from pymongo import ASCENDING
from ..event_handler import EventHandler, AppStartMessage, JobStartMessage, JobEndMessage, ResponseMessage, AppEndMessage
from .ellis_utils import EllisUtils


class EllisEventHandler(EventHandler):
    def __init__(self, db):
        self.db = db
        self.create_tables()
        self.ellis_utils = EllisUtils(db)

    def handle_application_start(self, message: AppStartMessage) -> ResponseMessage:
        app_id = self.insert_app_event(message)
        initial_scaleout = self.ellis_utils.compute_initial_scale_out(
            app_id, message.app_name, message.min_executors, message.max_executors, message.target_runtime
        )
        print(f"Recommending initial scale out: {initial_scaleout}")
        return ResponseMessage(
            app_event_id=app_id,
            recommended_scale_out=initial_scaleout
        )

    def handle_job_start(self, message: JobStartMessage) -> ResponseMessage:
        self.insert_job_event(message.app_event_id, message)
        return self.no_op_job_event_recommendation(message)

    def handle_job_end(self, message: JobEndMessage) -> ResponseMessage:
        self.update_job_event(message)

        (scaleOuts, _) = self.ellis_utils.get_non_adaptive_runs(message.app_event_id, message.app_name)
        if scaleOuts.size > 3:
            recommended_scale_out = self.ellis_utils.update_scaleout(
                message.app_event_id,
                message.job_id,
                message.app_time,
                message.num_executors
            )
            print(f"Recommending scale out: {recommended_scale_out}")
            return ResponseMessage(
                app_event_id=message.app_event_id,
                recommended_scale_out=recommended_scale_out,
            )
        else:
            return self.no_op_job_event_recommendation(message)

    def handle_application_end(self, message: AppEndMessage) -> ResponseMessage:
        self.db['app_event'].update_one(
            {'_id': message.app_event_id},
            {'$set': {'finished_at': message.app_time}}
        )
        return ResponseMessage(
            app_event_id=message.app_event_id,
            recommended_scale_out=message.num_executors,
        )

    def insert_app_event(self, message):
        result = self.db['app_event'].insert_one({
            'app_id': message.app_name,
            'started_at': message.app_time,
            'target_runtime': message.target_runtime,
            'initial_executors': message.initial_executors,
            'min_executors': message.min_executors,
            'max_executors': message.max_executors,
        })
        app_id = str(result.inserted_id)
        return app_id

    def insert_job_event(self, app_event_id, message):
        self.db['job_event'].insert_one({
            'app_event_id': app_event_id,
            'job_id': message.job_id,
            'started_at': message.app_time,
        })

    def update_job_event(self, message):

        job_event = self.db['job_event'].find_one({'app_event_id': message.app_event_id, 'job_id': message.job_id})
        finished_at = message.app_time
        duration = finished_at - job_event['started_at']

        self.db['job_event'].update_one(
            {'app_event_id': job_event['app_event_id'], 'job_id': job_event['job_id']},
            {'$set': {
                'finished_at': finished_at,
                'duration_ms': duration,
                'scale_out': message.num_executors,
            }}
        )

    def create_tables(self):
        self.db['app_event'].create_index(
            [('app_id', ASCENDING), ('started_at', ASCENDING)],
            unique=True
        )
        self.db['job_event'].create_index(
            [('app_event_id', ASCENDING), ('job_id', ASCENDING)],
            unique=True
        )
