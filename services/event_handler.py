import json
from typing import Dict, Optional, List
from enum import Enum
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class EventType(str, Enum):
    JOB_START = "JOB_START"
    JOB_END = "JOB_END"
    APPLICATION_START = "APPLICATION_START"
    APPLICATION_END = "APPLICATION_END"


class MessageEnvelope(BaseModel):
    event_type: EventType
    payload: dict

    @staticmethod
    def from_json(json_str: str) -> "MessageEnvelope":
        data = json.loads(json_str)
        data['event_type'] = EventType(data['event_type'])
        return MessageEnvelope(**data)


class EnvironmentSpecs(BaseModel):
    machine_type: str
    hadoop_version: str
    spark_version: str
    scala_version: str
    java_version: str


class DriverSpecs(BaseModel):
    cores: int
    memory: str
    memory_overhead: Optional[str] = None


class ExecutorSpecs(BaseModel):
    cores: int
    memory: str
    memory_overhead: Optional[str] = None


class AppSpecs(BaseModel):
    algorithm_name: str
    algorithm_args: List[str]
    datasize_mb: int
    target_runtime: int
    min_executors: int
    max_executors: int


class StageMetrics(BaseModel):
    cpu_utilization: float
    gc_time_ratio: float
    shuffle_read_write_ratio: float
    input_output_ratio: float
    memory_spill_ratio: float


class Stage(BaseModel):
    stage_id: str
    stage_name: str
    num_tasks: int
    parent_stage_ids: list[int]
    attempt_id: int
    failure_reason: str
    start_time: int
    end_time: int
    start_scale_out: int
    end_scale_out: int
    rescaling_time_ratio: float
    rdd_num_partitions: int
    rdd_num_cached_partitions: int
    rdd_mem_size: int
    rdd_disk_size: int
    metrics: StageMetrics


class AppStartMessage(BaseModel):
    application_id: str  # spark app id
    app_name: str  # spark app signature
    app_time: int
    is_adaptive: bool
    app_specs: AppSpecs
    driver_specs: DriverSpecs
    executor_specs: ExecutorSpecs
    environment_specs: EnvironmentSpecs

    @staticmethod
    def create(data: dict) -> "AppStartMessage":
        data['app_specs'] = AppSpecs(**data.get('app_specs', {}))
        data['driver_specs'] = DriverSpecs(**data.get('driver_specs', {}))
        data['executor_specs'] = ExecutorSpecs(**data.get('executor_specs', {}))
        data['environment_specs'] = EnvironmentSpecs(**data.get('environment_specs', {}))
        return AppStartMessage(**data)


class AppEndMessage(BaseModel):
    app_event_id: str
    app_time: int
    num_executors: int

    @staticmethod
    def create(data: dict) -> "AppEndMessage":
        return AppEndMessage(**data)


class JobStartMessage(BaseModel):
    app_event_id: str
    app_time: int
    job_id: int
    num_executors: int

    @staticmethod
    def create(data: dict) -> "JobStartMessage":
        return JobStartMessage(**data)


class JobEndMessage(BaseModel):
    app_event_id: str
    app_time: int
    job_id: int
    num_executors: int
    rescaling_time_ratio: float
    stages: Dict[str, Stage]

    @staticmethod
    def create(data: dict) -> "JobEndMessage":
        stages_data = data.pop("stages", {})
        stages = {key: Stage(**value) for key, value in stages_data.items()}
        return JobEndMessage(stages=stages, **data)


class ResponseMessage(BaseModel):
    app_event_id: str
    recommended_scale_out: int

    @staticmethod
    def create(json_str: str) -> "ResponseMessage":
        data = json.loads(json_str)
        return ResponseMessage(**data)


class EventHandler(ABC):
    """
    Interface for handling different Spark event types.
    """

    @abstractmethod
    def handle_application_start(self, message: AppStartMessage) -> ResponseMessage:
        pass

    @abstractmethod
    def handle_job_start(self, message: JobStartMessage) -> ResponseMessage:
        pass

    @abstractmethod
    def handle_job_end(self, message: JobEndMessage) -> ResponseMessage:
        pass

    @abstractmethod
    def handle_application_end(self, message: AppEndMessage) -> ResponseMessage:
        pass

    @staticmethod
    def no_op_app_start_response(message: AppStartMessage) -> ResponseMessage:
        return ResponseMessage(
            app_event_id="No_op_recommendation",
            recommended_scale_out=message.app_specs.min_executors,
        )

    @staticmethod
    def no_op_app_end_response(message: AppEndMessage) -> ResponseMessage:
        return ResponseMessage(
            app_event_id="No_op_recommendation",
            recommended_scale_out=message.num_executors,
        )

    @staticmethod
    def no_op_job_event_recommendation(message: JobStartMessage | JobEndMessage) -> ResponseMessage:
        return ResponseMessage(
            app_event_id=message.app_event_id,
            recommended_scale_out=message.num_executors
        )

# The NoOpEventHandler will recommend the minimum number of executors set in the app specs.
class NoOpEventHandler(EventHandler):

    def __init__(self, db):
        pass

    def handle_application_start(self, message: AppStartMessage) -> ResponseMessage:
        return self.no_op_app_start_response(message)

    def handle_job_start(self, message: JobStartMessage) -> ResponseMessage:
        return self.no_op_job_event_recommendation(message)

    def handle_job_end(self, message: JobEndMessage) -> ResponseMessage:
        return self.no_op_job_event_recommendation(message)

    def handle_application_end(self, message: AppEndMessage) -> ResponseMessage:
        return self.no_op_app_end_response(message)
