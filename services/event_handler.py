import json
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod


class EventType(Enum):
    JOB_START = "JOB_START"
    JOB_END = "JOB_END"
    APPLICATION_END = "APPLICATION_END"


@dataclass
class RequestMessage:
    app_id: str
    app_name: str
    app_time: int
    job_id: int
    num_executors: int
    event_type: EventType

    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        data['event_type'] = EventType(data['event_type'])
        return RequestMessage(**data)

    def to_json(self):
        data = asdict(self)
        data['event_type'] = self.event_type.value
        return json.dumps(data)


@dataclass
class ResponseMessage:
    app_id: str
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
    def handle_job_start(self, message: RequestMessage) -> ResponseMessage:
        pass

    @abstractmethod
    def handle_job_end(self, message: RequestMessage) -> ResponseMessage:
        pass

    @abstractmethod
    def handle_application_end(self, message: RequestMessage) -> ResponseMessage:
        pass
