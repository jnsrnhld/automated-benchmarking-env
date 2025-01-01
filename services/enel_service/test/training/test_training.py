import json
import os
from unittest import TestCase
from unittest.mock import MagicMock
from parameterized import parameterized
import sys
import pathlib

import ray

my_path = str(pathlib.Path(__file__).parents[4].absolute())
if my_path not in sys.path:
    sys.path.append(my_path)
    if my_path not in os.environ.get("PYTHONPATH", ""):
        os.environ["PYTHONPATH"] = my_path + ":" + os.environ.get("PYTHONPATH", "")

ray.init(local_mode=True)

from services.enel_service.config.onlinepredictor_config import OnlinePredictorConfig
from services.enel_service.common.async_utils import force_sync, async_return
from services.enel_service.modeling.handlers_training import handle_trigger_model_training
from services.enel_service.modeling.schemes import TriggerModelTrainingRequest
from services.enel_service.common.apis.fs_api import FsApi
from services.enel_service.common.apis.hdfs_api import HdfsApi
from services.enel_service.common.apis.mongo_api import MongoApi
from services.enel_service.common.configuration import MongoSettings, HdfsSettings

def transform_dates(input_dict):
    def update_dict(d):
        updated = {}
        for key, value in d.items():
            if isinstance(value, dict) and "$date" in value:
                # If the value contains $date, replace the parent key's value with the $date value
                updated[key] = value["$date"]
            elif isinstance(value, dict):  # If value is a nested dict, recurse
                updated[key] = update_dict(value)
            elif isinstance(value, list):  # If value is a list, process each element
                updated[key] = [update_dict(item) if isinstance(item, dict) else item for item in value]
            else:
                updated[key] = value  # Otherwise, keep the value as is
        return updated

    return update_dict(input_dict)


class TestTraining(TestCase):

    def setUp(self) -> None:
        self.fs_api = FsApi()
        self.mongo_api = MongoApi()
        self.mongo_settings = MongoSettings.get_instance()
        self.hdfs_api = HdfsApi()
        self.hdfs_settings = HdfsSettings.get_instance()
        self.onlinepredictor_config: OnlinePredictorConfig = OnlinePredictorConfig()
        self.onlinepredictor_config.model_setup["epochs"] = [30, 30]
        self.onlinepredictor_config.concurrency_limiter["max_concurrent"] = 1
        self.onlinepredictor_config.tune_run["num_samples"] = 1

    @parameterized.expand([
        ("ALS",
         "ALS with Params(hdfs://10.240.0.10:9000/HiBench/ALS/Input,10,0.1,10,1,1,true)",
         "als_job_execution.json"),
        ("DenseKMeans",
         "DenseKMeans with Params(hdfs://10.240.0.10:9000/HiBench/Kmeans/Input/samples,10,5,MEMORY_ONLY,Random)",
         "kmeans_job_execution.json"),
        ("RatingDataGeneration",
         "RatingDataGeneration",
         "rdg_job_execution.json")
    ])
    def test_training(self, algorithm_name, experiment_name, file_name):
        training_request = TriggerModelTrainingRequest(**{
            "system_name": "spark",
            "algorithm_name": algorithm_name,
            "model_name": "onlinepredictor",
            "experiment_name": experiment_name
        })

        job_executions = []
        with open(pathlib.Path(__file__).parent.joinpath(file_name), 'r') as job_execution:
            job_executions = json.load(job_execution)

        self.mongo_api.find = MagicMock(return_value=async_return([transform_dates(o) for o in job_executions]))
        force_sync(handle_trigger_model_training(training_request, self.mongo_api, self.hdfs_api,
                                                 onlinepredictor_config=self.onlinepredictor_config))
