import datetime

from pymongo import ASCENDING
from event_handler import EventHandler, RequestMessage, ResponseMessage
from ellis_port.ellis_utils import EllisUtils


class EllisEventHandler(EventHandler):
    def __init__(self, db):
        self.db = db
        self.create_tables()
        self.ellis_utils = EllisUtils(db)

    def handle_job_start(self, message: RequestMessage) -> ResponseMessage:

        if message.app_event_id:
            self.insert_job_event(message.app_event_id, message)
            return self.no_op_recommendation(message)

        else:
            app_id = self.insert_app_event(message)
            self.insert_job_event(app_id, message)

            return ResponseMessage(
                app_event_id=app_id,
                # no changes nor calculations required on JOB_START
                recommended_scale_out=message.num_executors
            )

    def handle_job_end(self, message: RequestMessage) -> ResponseMessage:

        job_events = self.db['job_event']
        job_event = job_events.find_one({'app_event_id': message.app_event_id, 'job_id': message.job_id})

        finished_at = EllisUtils.to_date_time(message.app_time)
        duration = (finished_at - job_event['started_at']).total_seconds() * 1000

        job_events.update_one(
            {'app_event_id': job_event['app_event_id'], 'job_id': job_event['job_id']},
            {'$set': {
                'finished_at': finished_at,
                'duration_ms': duration,
                'scale_out': message.num_executors,
            }}
        )

        return self.no_op_recommendation(message)

    def handle_application_end(self, message: RequestMessage) -> ResponseMessage:

        app_event_collection = self.db['app_event']
        app_event_collection.update_one(
            {'_id': message.app_event_id},
            {'$set': {'finished_at': EllisUtils.to_date_time(message.app_time)}}
        )

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

        return self.no_op_recommendation(message)

    def insert_app_event(self, message):
        app_event_document = {
            'app_id': message.app_name,
            'started_at': EllisUtils.to_date_time(message.app_time),
        }
        app_event_collection = self.db['app_event']
        result = app_event_collection.insert_one(app_event_document)
        app_id = str(result.inserted_id)
        return app_id

    def insert_job_event(self, app_event_id, message):
        job_event_document = {
            'app_event_id': app_event_id,
            'job_id': message.job_id,
            'started_at': EllisUtils.to_date_time(message.app_time),
        }
        job_event_collection = self.db['job_event']
        job_event_collection.insert_one(job_event_document)

    def create_tables(self):
        app_event_collection = self.db['app_event']
        app_event_collection.create_index(
            [('app_id', ASCENDING), ('started_at', ASCENDING)],
            unique=True
        )

        job_event_collection = self.db['job_event']
        job_event_collection.create_index(
            [('app_event_id', ASCENDING), ('job_id', ASCENDING)],
            unique=True
        )
