import uuid

from event_handler import EventHandler
from event_handler import RequestMessage
from event_handler import ResponseMessage


class NoOpEventHandler(EventHandler):

    def handle_job_start(self, message: RequestMessage) -> ResponseMessage:
        return self.no_op_recommendation(message)

    def handle_job_end(self, message: RequestMessage) -> ResponseMessage:
        return self.no_op_recommendation(message)

    def handle_application_end(self, message: RequestMessage) -> ResponseMessage:
        return self.no_op_recommendation(message)

    @staticmethod
    def no_op_recommendation(message):
        app_id = message.app_id or str(uuid.uuid4())
        recommended_scale_out = message.num_executors
        return ResponseMessage(app_id=app_id, recommended_scale_out=recommended_scale_out)
