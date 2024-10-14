import json
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
class JobEventMessage:
    app_event_id: str
    app_name: str
    app_time: int
    job_id: int
    num_executors: int

    @staticmethod
    def create(data: dict):
        return JobEventMessage(**data)

    def to_json(self):
        return json.dumps(asdict(self))


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
    def handle_job_start(self, message: JobEventMessage) -> ResponseMessage:
        pass

    @abstractmethod
    def handle_job_end(self, message: JobEventMessage) -> ResponseMessage:
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
    def no_op_job_event_recommendation(message: JobEventMessage) -> ResponseMessage:
        return ResponseMessage(
            app_event_id=message.app_event_id,
            recommended_scale_out=message.num_executors
        )


class NoOpEventHandler(EventHandler):

    def __init__(self, db):
        pass

    def handle_application_start(self, message: AppStartMessage) -> ResponseMessage:
        return self.no_op_app_start_response(message)

    def handle_job_start(self, message: JobEventMessage) -> ResponseMessage:
        return self.no_op_job_event_recommendation(message)

    def handle_job_end(self, message: JobEventMessage) -> ResponseMessage:
        return self.no_op_job_event_recommendation(message)

    def handle_application_end(self, message: AppEndMessage) -> ResponseMessage:
        return self.no_op_app_end_response(message)
