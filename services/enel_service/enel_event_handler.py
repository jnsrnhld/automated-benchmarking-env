import asyncio
import threading

from bson.objectid import ObjectId
from pydantic import BaseModel

from .modeling.handlers_training import handle_trigger_model_training
from .common.db_schemes import ApplicationExecutionModel, GlobalSpecsModel, OptionalSpecsModel, MasterSpecsModel, \
    WorkerSpecsModel
from .submission.handlers import alter_submission_model
from .modeling.handlers_scale_out import handle_online_scale_out_prediction
from .modeling.schemes import UpdateInformationRequest, RootDataUpdateModel, OnlineScaleOutPredictionRequest, TriggerModelTrainingRequest
from .modeling.handlers_updating import handle_update_information
from .common.apis.hdfs_api import HdfsApi
from .common.apis.mongo_api import MongoApi
from ..event_handler import EventHandler, AppEndMessage, ResponseMessage, JobEndMessage, JobStartMessage, \
    AppStartMessage, EventType, Stage

def run_async_in_background(coroutine):
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=loop.run_until_complete, args=(coroutine,))
    thread.daemon = True
    thread.start()

class EnelEventHandler(EventHandler):
    def __init__(self):
        self.mongo_api = MongoApi()
        self.hdfs_api = HdfsApi()
        self.running_applications: dict[str, RunningApplication] = {}
        pass

    def handle_application_start(self, message: AppStartMessage) -> ResponseMessage:

        app_event_id = str(ObjectId())
        application = RunningApplication(app_event_id, message)
        self.running_applications[app_event_id] = application

        # add the application
        application_execution_model = application.to_application_execution_model(message)
        app_model: ApplicationExecutionModel = asyncio.run(
            alter_submission_model(application_execution_model, self.hdfs_api, self.mongo_api)
        )
        initial_scaleout = app_model.worker_specs.scale_out
        application.scale_out_map[0] = initial_scaleout

        # update it
        update_request = application.to_update_information_request(message)
        asyncio.run(handle_update_information(update_request, self.mongo_api))

        if message.is_training:
            training_request = application.to_trigger_model_training_request(application_execution_model)
            run_async_in_background(handle_trigger_model_training(training_request, self.mongo_api, self.hdfs_api))

        print(f"Recommending initial scale-out: {initial_scaleout}")

        return ResponseMessage(
            app_event_id=app_event_id,
            recommended_scale_out=initial_scaleout
        )

    def handle_job_start(self, message: JobStartMessage) -> ResponseMessage:
        self.add_job(message)
        return self.no_op_job_event_recommendation(message)

    def handle_job_end(self, message: JobEndMessage) -> ResponseMessage:

        self.update_job(message)
        job_id = message.job_id
        next_job_id = job_id + 1
        application = self.running_applications.get(message.app_event_id)
        app_scale_out_map = application.scale_out_map
        app_scale_out_map[next_job_id] = app_scale_out_map.get(next_job_id, app_scale_out_map.get(job_id))

        application.try_handle_online_scale_out_request(message, self.hdfs_api, self.mongo_api)

        if app_scale_out_map[next_job_id] != app_scale_out_map.get(job_id):
            print(f"Recommending next scale-out: {app_scale_out_map[next_job_id]}")
            return ResponseMessage(
                app_event_id=message.app_event_id,
                recommended_scale_out=app_scale_out_map[next_job_id],
            )
        else:
            print(f"Scale-out same in next job...")
            return self.no_op_job_event_recommendation(message)

    def handle_application_end(self, message: AppEndMessage) -> ResponseMessage:
        # spark applications are handled sequentially - we can just clear state, and we are ready for another job
        self.running_applications.pop(message.app_event_id)
        return self.no_op_app_end_response(message)

    def add_job(self, message: JobStartMessage):
        job_info = JobInfo(
            job_id=message.job_id,
            start_time=message.app_time,
            start_scale_out=message.num_executors,
            stages={}
        )
        self.running_applications.get(message.app_event_id).put_info_map(message.job_id, job_info)

    def update_job(self, message: JobEndMessage):
        application = self.running_applications.get(message.app_event_id)
        job_info = application.job_info_map.get(application.to_map_key(message.job_id))
        job_info.end_time = message.app_time
        job_info.end_scale_out = message.num_executors
        job_info.predicted_scale_out = application.scale_out_map.get(message.job_id)
        job_info.rescaling_time_ratio = message.rescaling_time_ratio
        job_info.stages = message.stages

class JobInfo(BaseModel):
    job_id: int
    start_time: int
    start_scale_out: int
    end_time: int = None
    end_scale_out: int = None
    predicted_scale_out: int = None
    rescaling_time_ratio: float = None
    stages: dict[str, Stage]

class RunningApplication:
    def __init__(self, app_event_id: str, app_start_message: AppStartMessage):
        self.is_adaptive = app_start_message.is_adaptive
        self.app_event_id = app_event_id
        self.application_id = app_event_id
        self.app_signature = app_start_message.app_name
        self.job_info_map: dict[str, JobInfo] = {}
        self.scale_out_map: dict[int, int] = {}
        self.lastPredictionLength = -1

    def put_info_map(self, job_id: int, job_info: JobInfo):
        map_key = self.to_map_key(job_id)
        self.job_info_map[map_key] = job_info

    def to_map_key(self, job_id: int):
        return f"appId={self.application_id}-jobId={job_id}"

    def try_handle_online_scale_out_request(self, message, hdfs_api: HdfsApi, mongo_api: MongoApi):

        request_prediction = self.is_adaptive
        prediction_request = self.to_online_scale_out_prediction_request(message.job_id, request_prediction)
        prediction_response = asyncio.run(
            handle_online_scale_out_prediction(prediction_request, None, hdfs_api, mongo_api)
        )

        remaining_jobs = list(filter(
            lambda _tuple: _tuple[0] >= message.job_id,
            prediction_response.best_predicted_scale_out_per_job
        ))

        # last job, skip update of predicted scale outs
        if len(remaining_jobs) == 0:
            return

        remaining_jobs = list(sorted(
            remaining_jobs,
            key=lambda _tuple: _tuple[0]
        ))

        best_scale_out_per_job = prediction_response.best_predicted_scale_out_per_job
        if self.lastPredictionLength == -1 or self.lastPredictionLength > len(best_scale_out_per_job):
            self.lastPredictionLength = len(best_scale_out_per_job)
            for sub_list in remaining_jobs:
                if sub_list[0] == (message.job_id + 1):
                    # Update the predicted scale-out map
                    self.scale_out_map[sub_list[0]] = sub_list[-1]

    def to_online_scale_out_prediction_request(self, job_id: int, request_prediction: bool) -> OnlineScaleOutPredictionRequest:
        job_info = self.job_info_map.get(self.to_map_key(job_id))
        return OnlineScaleOutPredictionRequest(
            application_execution_id=self.app_event_id,
            application_id=self.app_event_id,
            job_id=job_id,
            update_event=EventType.JOB_END,
            updates=RootDataUpdateModel(**job_info.dict()),
            predict=request_prediction
        )

    def to_update_information_request(self, message: AppStartMessage):
        return UpdateInformationRequest(
            application_execution_id=self.app_event_id,
            application_id=self.app_event_id,
            update_event=EventType.APPLICATION_START,
            updates=(RootDataUpdateModel(
                application_id=self.app_event_id,
                application_signature=message.app_name,
                start_time=message.app_time,
            )),
        )

    def to_application_execution_model(self, message: AppStartMessage) -> ApplicationExecutionModel:
        return ApplicationExecutionModel(
            _id=self.app_event_id,
            start_scale_out=1, # placeholder, will be overwritten
            end_scale_out=1, # placeholder, will be overwritten
            global_specs=GlobalSpecsModel(
                solution_name="enel",
                system_name="spark",
                is_adaptive=message.is_adaptive,
                experiment_name=message.app_name,
                algorithm_name=message.app_specs.algorithm_name,
                algorithm_args=message.app_specs.algorithm_args,
                data_size_MB=message.app_specs.datasize_mb,
                machine_name=message.environment_specs.machine_type,
                min_scale_out=message.app_specs.min_executors,
                max_scale_out=message.app_specs.max_executors,
                max_runtime=message.app_specs.target_runtime,
            ),
            optional_specs=OptionalSpecsModel(
                hadoop_version=message.environment_specs.hadoop_version,
                spark_version=message.environment_specs.spark_version,
                scala_version=message.environment_specs.scala_version,
                java_version=message.environment_specs.java_version,
            ),
            master_specs=MasterSpecsModel(
                cores=message.driver_specs.cores,
                memory=message.driver_specs.memory,
                memory_overhead=message.driver_specs.memory_overhead,
            ),
            worker_specs=WorkerSpecsModel(
                cores=message.executor_specs.cores,
                memory=message.executor_specs.memory,
                memory_overhead=message.executor_specs.memory_overhead,
            ),
        )

    def to_trigger_model_training_request(self, app_model: ApplicationExecutionModel) -> TriggerModelTrainingRequest:
        return TriggerModelTrainingRequest(
            system_name=app_model.global_specs.system_name,
            algorithm_name=app_model.global_specs.algorithm_name,
            model_name="onlinepredictor",
            experiment_name=app_model.global_specs.experiment_name,
        )
