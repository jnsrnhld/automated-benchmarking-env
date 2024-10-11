import datetime

from pymongo import ASCENDING
from event_handler import EventHandler
from event_handler import RequestMessage
from event_handler import ResponseMessage


class EllisEventHandler(EventHandler):
    def __init__(self, db):
        self.db = db
        self.create_tables()

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

        finished_at = EllisEventHandler.to_date_time(message.app_time)
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
            {'$set': {'finished_at': EllisEventHandler.to_date_time(message.app_time)}}
        )

        # TODO handle actual prediction

        return self.no_op_recommendation(message)

    def insert_app_event(self, message):
        app_event_document = {
            'app_id': message.app_name,
            'started_at': EllisEventHandler.to_date_time(message.app_time),
        }
        app_event_collection = self.db['app_event']
        result = app_event_collection.insert_one(app_event_document)
        app_id = str(result.inserted_id)
        return app_id

    def insert_job_event(self, app_event_id, message):
        job_event_document = {
            'app_event_id': app_event_id,
            'job_id': message.job_id,
            'started_at': EllisEventHandler.to_date_time(message.app_time),
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

    @staticmethod
    def to_date_time(time: int) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(time / 1000.0, datetime.timezone.utc)
