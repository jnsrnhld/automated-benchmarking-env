from pymongo import MongoClient, ASCENDING

from services.event_handler import EventHandler, AppStartMessage, JobStartMessage, JobEndMessage, ResponseMessage, \
    AppEndMessage
from .ellis_utils import EllisUtils
from .config import Config


def connect_to_mongodb():
    try:
        client = MongoClient(Config.MONGODB_CONNECTION_STRING, tz_aware=True)
        db = client[Config.MONGODB_DATABASE]
        print(f"Connected to MongoDB database: {Config.MONGODB_DATABASE}")
        return db
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise


class EllisEventHandler(EventHandler):
    def __init__(self):
        self.db = connect_to_mongodb()
        self.create_tables()
        self.ellis_utils = EllisUtils(self.db)
        self.running_applications: dict[str, RunningApplication] = {}

    def handle_application_start(self, message: AppStartMessage) -> ResponseMessage:

        app_event_id = self.insert_app_event(message)
        app_specs = message.app_specs
        initial_scaleout = self.ellis_utils.compute_initial_scale_out(
            app_event_id, message.app_name, app_specs.min_executors, app_specs.max_executors, app_specs.target_runtime
        )
        self.running_applications[app_event_id] = RunningApplication(message.application_id, app_event_id, message.app_name)
        print(f"Recommending initial scale out: {initial_scaleout}")

        return ResponseMessage(
            app_event_id=app_event_id,
            recommended_scale_out=initial_scaleout
        )

    def handle_job_start(self, message: JobStartMessage) -> ResponseMessage:
        self.insert_job_event(message.app_event_id, message)
        return self.no_op_job_event_recommendation(message)

    def handle_job_end(self, message: JobEndMessage) -> ResponseMessage:
        self.update_job_event(message)

        running_app = self.running_applications[message.app_event_id]
        (scaleOuts, _) = self.ellis_utils.get_non_adaptive_runs(running_app.app_event_id, running_app.app_signature)
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

        self.db[Config.ELLIS_APP_EVENT_COLLECTION].update_one(
            {'_id': message.app_event_id},
            {'$set': {'finished_at': message.app_time}}
        )
        self.running_applications.pop(message.app_event_id)

        return ResponseMessage(
            app_event_id=message.app_event_id,
            recommended_scale_out=message.num_executors,
        )

    def insert_app_event(self, message: AppStartMessage):
        result = self.db[Config.ELLIS_APP_EVENT_COLLECTION].insert_one({
            'app_id': message.app_name,
            'started_at': message.app_time,
            'target_runtime': message.app_specs.target_runtime,
            'initial_executors': message.app_specs.initial_executors,
            'min_executors': message.app_specs.min_executors,
            'max_executors': message.app_specs.max_executors,
        })
        app_id = str(result.inserted_id)
        return app_id

    def insert_job_event(self, app_event_id, message):
        self.db[Config.ELLIS_JOB_EVENT_COLLECTION].insert_one({
            'app_event_id': app_event_id,
            'job_id': message.job_id,
            'started_at': message.app_time,
        })

    def update_job_event(self, message):

        job_event = self.db[Config.ELLIS_JOB_EVENT_COLLECTION].find_one(
            {'app_event_id': message.app_event_id, 'job_id': message.job_id}
        )
        finished_at = message.app_time
        duration = finished_at - job_event['started_at']

        self.db[Config.ELLIS_JOB_EVENT_COLLECTION].update_one(
            {'app_event_id': job_event['app_event_id'], 'job_id': job_event['job_id']},
            {'$set': {
                'finished_at': finished_at,
                'duration_ms': duration,
                'scale_out': message.num_executors,
            }}
        )

    def create_tables(self):
        self.db[Config.ELLIS_APP_EVENT_COLLECTION].create_index(
            [('app_id', ASCENDING), ('started_at', ASCENDING)],
            unique=True
        )
        self.db[Config.ELLIS_JOB_EVENT_COLLECTION].create_index(
            [('app_event_id', ASCENDING), ('job_id', ASCENDING)],
            unique=True
        )

class RunningApplication():
    def __init__(self, application_id: str, app_event_id: str, app_signature: str):
        self.application_id = application_id
        self.app_event_id = app_event_id
        self.app_signature = app_signature
