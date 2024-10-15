import json
from typing import List
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod


class EventType(Enum):
    JOB_START = "JOB_START"
    JOB_END = "JOB_END"
    APPLICATION_START = "APPLICATION_START"
    APPLICATION_END = "APPLICATION_END"


@dataclass
class MessageEnvelope:
    event_type: EventType
    payload: dict

    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        data['event_type'] = EventType(data['event_type'])
        return MessageEnvelope(**data)

    def to_json(self):
        data = asdict(self)
        data['event_type'] = self.event_type.value
        return json.dumps(data)


@dataclass
class AppStartMessage:
    app_name: str
    app_time: int
    target_runtime: int
    initial_executors: int
    min_executors: int
    max_executors: int
    attempt_id: str

    @staticmethod
    def create(data: dict):
        return AppStartMessage(**data)

    def to_json(self):
        return json.dumps(asdict(self))


@dataclass
class AppEndMessage:
    app_event_id: str
    app_name: str
    app_time: int
    num_executors: int

    @staticmethod
    def create(data: dict):
        return AppEndMessage(**data)

    def to_json(self):
        return json.dumps(asdict(self))


@dataclass
class JobStartMessage:
    app_event_id: str
    app_name: str
    app_time: int
    job_id: int
    num_executors: int

    @staticmethod
    def create(data: dict):
        return JobStartMessage(**data)

    def to_json(self):
        return json.dumps(asdict(self))


@dataclass
class StageMetrics:
    cpu_utilization: float
    gc_time_ratio: float
    shuffle_read_write_ratio: float
    input_output_ratio: float
    memory_spill_ratio: float


@dataclass
class Stage:
    stage_id: str
    stage_name: str
    num_tasks: int
    parent_stage_ids: str
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


@dataclass
class JobEndMessage:
    app_event_id: str
    app_name: str
    app_time: int
    job_id: int
    num_executors: int
    rescaling_time_ratio: float
    stages: List[Stage]

    @staticmethod
    def create(data: dict):
        stages_data = data.pop("stages", [])
        stages = [Stage(**stage_data) for stage_data in stages_data]
        return JobEndMessage(stages=stages, **data)

    def to_json(self):
        return json.dumps(asdict(self), indent=4)


@dataclass
class ResponseMessage:
    app_event_id: str
    recommended_scale_out: int

    @staticmethod
    def create(json_str):
        data = json.loads(json_str)
        return ResponseMessage(**data)

    def to_json(self):
        return json.dumps(asdict(self))


class EventHandler(ABC):
    """
    Interface for handling different event types.
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
            recommended_scale_out=message.initial_executors,
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
