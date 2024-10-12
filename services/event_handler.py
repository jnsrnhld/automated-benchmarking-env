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
class AppRequestMessage:
    app_name: str
    app_time: int
    target_runtime: int
    initial_executors: int
    min_executors: int
    max_executors: int

    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        return AppRequestMessage(**data)

    def to_json(self):
        return json.dumps(asdict(self))


@dataclass
class JobRequestMessage:
    app_event_id: str
    app_name: str
    app_time: int
    job_id: int
    num_executors: int

    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        return JobRequestMessage(**data)

    def to_json(self):
        return json.dumps(asdict(self))


@dataclass
class ResponseMessage:
    app_event_id: str
    recommended_scale_out: int

    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        return ResponseMessage(**data)

    def to_json(self):
        return json.dumps(asdict(self))


class EventHandler(ABC):
    """
    Interface for handling different event types.
    """

    @abstractmethod
    def handle_job_start(self, message: JobRequestMessage) -> ResponseMessage:
        pass

    @abstractmethod
    def handle_job_end(self, message: JobRequestMessage) -> ResponseMessage:
        pass

    @abstractmethod
    def handle_application_start(self, message: AppRequestMessage) -> ResponseMessage:
        pass

    @abstractmethod
    def handle_application_end(self, message: AppRequestMessage) -> ResponseMessage:
        pass

    @staticmethod
    def no_op_recommendation(message):
        return ResponseMessage(
            app_event_id=message.app_event_id,
            recommended_scale_out=message.num_executors
        )
