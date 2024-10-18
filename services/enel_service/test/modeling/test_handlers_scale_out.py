# noinspection DuplicatedCode
import copy
from contextlib import redirect_stderr
from io import StringIO
from typing import List
from unittest import TestCase
from unittest.mock import MagicMock, Mock, AsyncMock, patch, ANY

from fastapi import BackgroundTasks

from services.enel_service.modeling import request_id, application_database_obj, job_database_obj
from services.enel_service.common.apis.hdfs_api import HdfsApi
from services.enel_service.common.apis.mongo_api import MongoApi
from services.enel_service.common.async_utils import async_return, force_sync
from services.enel_service.common.configuration import MongoSettings, HdfsSettings
from services.enel_service.common.db_schemes import JobExecutionModel
from services.enel_service.config.onlinepredictor_config import OnlinePredictorConfig
from services.enel_service.modeling.handlers_scale_out import handle_online_scale_out_prediction
from services.enel_service.modeling.handlers_updating import update_job_object
from services.enel_service.modeling.model_wrappers import OnlinePredictorModel
from services.enel_service.modeling.schemes import OnlineScaleOutPredictionRequest, RootDataUpdateModel
from services.enel_service.modeling.transforms import CustomCompose
from services.enel_service.modeling.utils import reset_artifact_cache, prepare_for_inference


class TestHandleOnlineScaleOutPrediction(TestCase):
    def setUp(self) -> None:
        self.background_tasks = BackgroundTasks()
        self.key_prefix: str = f"spark_grep_onlinepredictor"
        self.stage_id: str = "002"
        self.request_id: str = copy.deepcopy(request_id)
        self.app_database_obj = copy.deepcopy(application_database_obj)
        self.job_database_obj = copy.deepcopy(job_database_obj)

        # Prepare updates data
        updates_data = {
            "start_scale_out": 1,
            "end_scale_out": 1,
            "global_specs": {
                "solution_name": "enel",
                "system_name": "spark",
                "template_version": "v1",
                "experiment_name": "test_experiment",
                "algorithm_name": "grep",
                "algorithm_args": [],
                "data_size_MB": 100,
                "data_characteristics": "",
                "machine_name": "machine_1",
                "environment_name": "env_1",
                "min_scale_out": 1,
                "max_scale_out": 5,
                "max_runtime": 60
            },
            "optional_specs": {
                "hadoop_version": None,
                "spark_version": None,
                "scala_version": None,
                "java_version": None
            },
            "master_specs": {
                "scale_out": 1,
                "cores": 4,
                "memory": "8g",
                "memory_overhead": "1g"
            },
            "worker_specs": {
                "scale_out": 1,
                "cores": 4,
                "memory": "8g",
                "memory_overhead": "1g"
            },
            "flink_template_values": {},
            "spark_template_values": {},
            "id": "some_id",
            "attempt_id": "attempt_1",
            "predicted_scale_out": 1,
            "application_execution_id": self.request_id,
            "job_id": 1,
            "stages": {},
            "rescaling_time_ratio": 0.0
        }

        updates_model = RootDataUpdateModel(**updates_data)

        self.request = OnlineScaleOutPredictionRequest(
            application_execution_id=self.request_id,
            application_id="app123",
            job_id=1,
            update_event="JOB_END",
            updates=updates_model,
            predict=True
        )

        self.mongo_api = MongoApi()
        self.mongo_settings = MongoSettings.get_instance()
        self.hdfs_api = HdfsApi()
        self.hdfs_settings = HdfsSettings.get_instance()
        # reset cache
        reset_artifact_cache()

    def test_only_update(self):
        self.request.predict = False
        self.background_tasks.add_task = Mock()

        with redirect_stderr(StringIO()) as _:
            response = force_sync(handle_online_scale_out_prediction(self.request, self.background_tasks,
                                                                     self.hdfs_api, self.mongo_api))
            self.assertTrue(isinstance(response.best_predicted_scale_out_per_job, list))
            self.assertTrue(isinstance(response.best_predicted_runtime_per_job, list))
            self.background_tasks.add_task.assert_called_once()

    def test_prediction_ok_without_history(self):
        onlinepredictor_config: OnlinePredictorConfig = OnlinePredictorConfig()
        onlinepredictor_config.model_setup["epochs"] = [20, 20]

        # create artifacts
        data_transformer: CustomCompose = CustomCompose(transformer_specs=onlinepredictor_config.transformer_specs)
        model_wrapper = OnlinePredictorModel(onlinepredictor_config)
        torchscript_model = model_wrapper.get_torchscript_model_instance()

        # fit data transformer
        successor_jobs: List[JobExecutionModel] = [
            JobExecutionModel(**{**self.job_database_obj, "job_id": self.job_database_obj["job_id"] + 1}),
            JobExecutionModel(**{**self.job_database_obj, "job_id": self.job_database_obj["job_id"] + 2})
        ]
        _, eval_data, _ = prepare_for_inference(JobExecutionModel(**self.job_database_obj), "online", successor_jobs)
        data_transformer.fit(eval_data)

        self.background_tasks.add_task = Mock()

        with patch('motor.motor_asyncio.AsyncIOMotorClient', new_callable=AsyncMock) as client:
            self.mongo_api.client = client
            # mock certain behavior
            self.mongo_api.close_client = AsyncMock()
            self.mongo_api.find_one = Mock()
            self.mongo_api.find_one.side_effect = [async_return(self.app_database_obj),
                                                   async_return(self.job_database_obj),
                                                   async_return(self.app_database_obj),
                                                   async_return(self.job_database_obj)]
            self.mongo_api.find = Mock()
            self.mongo_api.aggregate = MagicMock(return_value=async_return([]))
            self.mongo_api.find.side_effect = [
                async_return([]),  # we do not find any historical data
                async_return([
                    {**self.job_database_obj, "job_id": self.job_database_obj["job_id"] + 1},
                    {**self.job_database_obj, "job_id": self.job_database_obj["job_id"] + 2}
                ])
            ]
            self.mongo_api.update_one = MagicMock(return_value=async_return(True))

            session_mock = AsyncMock()
            client.configure_mock(**{
                "start_session.return_value.__aexit__.return_value": session_mock,
                "start_session.return_value.__aenter__.return_value": MagicMock(**{
                    "with_transaction.return_value": AsyncMock(
                        return_value=force_sync(update_job_object(self.request, self.mongo_api, session_mock))),
                })
            })

            self.hdfs_api.exists_file = MagicMock(return_value=True)
            self.hdfs_api.load = Mock()
            self.hdfs_api.load.side_effect = [
                ({}, False),  # empty checkpoint
                (data_transformer, False),
                (model_wrapper, False),
                (torchscript_model, False)
            ]

            with redirect_stderr(StringIO()) as _:
                force_sync(handle_online_scale_out_prediction(self.request, self.background_tasks,
                                                              self.hdfs_api, self.mongo_api))
                self.background_tasks.add_task.assert_not_called()

                self.mongo_api.aggregate.assert_not_called()
                # once for transaction
                self.mongo_api.close_client.assert_called_once()
