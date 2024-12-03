from unittest import TestCase

from bson.json_util import ObjectId

from services.enel_service.common.db_schemes import GlobalSpecsModel, OptionalSpecsModel, MasterSpecsModel, WorkerSpecsModel
from services.event_handler import AppStartMessage
from services.enel_service.common.db_schemes import ApplicationExecutionModel
from services.enel_service.enel_event_handler import JobInfo
from services.enel_service.modeling.schemes import OnlineScaleOutPredictionRequest, RootDataUpdateModel, \
    UpdateInformationRequest
from services.event_handler import JobStartMessage, JobEndMessage, EventType


class TestSchemes(TestCase):

    def setUp(self):
        self.app_start_message = {
            "application_id": "spark-a8c3067a1e2b4d8ab95f823629fae268",
            "app_name": "ALS with Params(hdfs://10.240.0.10:9000/HiBench/ALS/Input,10,0.1,10,1,1,true)",
            "app_time": 1729963312309,
            "attempt_id": None,
            "is_adaptive": True,
            "app_specs": {
                "algorithm_name": "ALS ",
                "algorithm_args": [
                    "hdfs://10.240.0.10:9000/HiBench/ALS/Input",
                    "10",
                    "0.1",
                    "10",
                    "1",
                    "1",
                    "true"
                ],
                "datasize_mb": 1,
                "target_runtime": 50000,
                "initial_executors": 2,
                "min_executors": 1,
                "max_executors": 3
            },
            "driver_specs": {
                "cores": 1,
                "memory": "8192m",
                "memory_overhead": "820m"
            },
            "executor_specs": {
                "cores": 1,
                "memory": "8192m",
                "memory_overhead": "820m"
            },
            "environment_specs": {
                "machine_type": "os:GNU/LinuxUbuntu20.04.6LTS(FocalFossa)build6.8.0-1016-gcp-cores:4-memory:32094.5703125-disk_size:125.0",
                "hadoop_version": "3.3.6", "spark_version": "3.5.3", "scala_version": "2.12.20",
                "java_version": "8"
            }
        }
        self.job_start_message = {
            "app_event_id": "671bed3f2382960e41b5d067",
            "app_time": 1729883464570,
            "job_id": 0,
            "num_executors": 2
        }
        self.job_end_message = {
            "app_event_id": "671bed3f2382960e41b5d067",
            "app_time": 1729883466722,
            "job_id": 0,
            "num_executors": 2,
            "rescaling_time_ratio": 0.0,
            "stages": {
                "0": {
                    "stage_id": "0",
                    "stage_name": "isEmpty at ALS.scala:975",
                    "num_tasks": 1,
                    "parent_stage_ids": [],
                    "attempt_id": 0,
                    "failure_reason": "",
                    "start_time": 1729883464597,
                    "end_time": 1729883466713,
                    "start_scale_out": 2,
                    "end_scale_out": 2,
                    "rescaling_time_ratio": 0.0,
                    "rdd_num_partitions": 8,
                    "rdd_num_cached_partitions": 2,
                    "rdd_mem_size": 64,
                    "rdd_disk_size": 1028,
                    "metrics": {
                        "cpu_utilization": 64.0,
                        "gc_time_ratio": 0.0,
                        "shuffle_read_write_ratio": 0.0,
                        "input_output_ratio": 0.5,
                        "memory_spill_ratio": 0.1,
                    }
                }
            }
        }

    def test_create_OnlineScaleOutPredictionRequest(self):
        job_start_message = JobStartMessage.create(self.job_start_message)
        job_end_message = JobEndMessage.create(self.job_end_message)
        job_info = JobInfo(
            job_id=job_start_message.job_id,
            start_time=job_start_message.app_time,
            start_scale_out=job_start_message.num_executors,
            stages={}
        )
        job_info.end_time = job_end_message.app_time
        job_info.end_scale_out = job_end_message.num_executors
        job_info.predicted_scale_out = 5
        job_info.rescaling_time_ratio = job_end_message.rescaling_time_ratio
        job_info.stages = job_end_message.stages

        prediction_request = OnlineScaleOutPredictionRequest(
            application_execution_id=str(ObjectId()),
            application_id='spark-1507b4a9d85d4deb888c6a5f03e7c612',
            update_event=EventType.JOB_END,
            updates=RootDataUpdateModel(**job_info.dict()),
            predict=True
        )

        print(f"prediction_request: {prediction_request.json()}")

        update_information_request = UpdateInformationRequest(**prediction_request.dict())
        print(f"update_information_request: {update_information_request.json()}")

        app_start_message = AppStartMessage.create(self.app_start_message)
        ApplicationExecutionModel(
            _id=str(ObjectId()),
            start_scale_out=app_start_message.app_specs.initial_executors,  # will be overridden eventually
            end_scale_out=app_start_message.app_specs.initial_executors,  # will be overridden eventually
            global_specs=GlobalSpecsModel(
                is_adaptive=True,
                solution_name="enel",
                system_name="spark",
                experiment_name=app_start_message.app_name,
                algorithm_name=app_start_message.app_specs.algorithm_name,
                algorithm_args=app_start_message.app_specs.algorithm_args,
                data_size_MB=app_start_message.app_specs.datasize_mb,
                machine_name=app_start_message.environment_specs.machine_type,
                min_scale_out=app_start_message.app_specs.min_executors,
                max_scale_out=app_start_message.app_specs.max_executors,
                max_runtime=app_start_message.app_specs.target_runtime,
            ),
            optional_specs=OptionalSpecsModel(
                hadoop_version=app_start_message.environment_specs.hadoop_version,
                spark_version=app_start_message.environment_specs.spark_version,
                scala_version=app_start_message.environment_specs.scala_version,
                java_version=app_start_message.environment_specs.java_version,
            ),
            master_specs=MasterSpecsModel(
                cores=app_start_message.driver_specs.cores,
                memory=app_start_message.driver_specs.memory,
                memory_overhead=app_start_message.driver_specs.memory_overhead,
            ),
            worker_specs=WorkerSpecsModel(
                cores=app_start_message.executor_specs.cores,
                memory=app_start_message.executor_specs.memory,
                memory_overhead=app_start_message.executor_specs.memory_overhead,
            ),
        )

        assert True
