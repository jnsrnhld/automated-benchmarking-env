import uuid

from event_handler import EventHandler, RequestMessage, ResponseMessage


class NoOpEventHandler(EventHandler):

    def __init__(self, db):
        pass

    def handle_job_start(self, message: RequestMessage) -> ResponseMessage:
        return self.no_op_recommendation(message)

    def handle_job_end(self, message: RequestMessage) -> ResponseMessage:
        return self.no_op_recommendation(message)

    def handle_application_end(self, message: RequestMessage) -> ResponseMessage:
        return self.no_op_recommendation(message)
