import json
from unittest import TestCase
from unittest.mock import MagicMock

from services.enel_service.common.async_utils import force_sync, async_return
from services.enel_service.modeling.handlers_training import handle_trigger_model_training
from services.enel_service.modeling.schemes import TriggerModelTrainingRequest
from services.enel_service.common.apis.fs_api import FsApi
from services.enel_service.common.apis.hdfs_api import HdfsApi
from services.enel_service.common.apis.mongo_api import MongoApi
from services.enel_service.common.configuration import MongoSettings, HdfsSettings


class TestTraining(TestCase):

    def setUp(self) -> None:
        self.fs_api = FsApi()
        self.mongo_api = MongoApi()
        self.mongo_settings = MongoSettings.get_instance()
        self.hdfs_api = HdfsApi()
        self.hdfs_settings = HdfsSettings.get_instance()
        self.training_request = TriggerModelTrainingRequest(**{
            "system_name": "spark",
            "algorithm_name": "ALS",
            "model_name": "onlinepredictor",
            "experiment_name": "ALS with Params(hdfs://10.240.0.10:9000/HiBench/ALS/Input,10,0.1,10,1,1,true)"
        })

        with open('services/enel_service/test/training/job_execution.json', 'r') as job_execution:
            self.job_executions = json.load(job_execution)

    def test_training(self):
        self.mongo_api.find = MagicMock(return_value=async_return([self.job_executions]))
        force_sync(handle_trigger_model_training(self.training_request, self.mongo_api, self.hdfs_api))
