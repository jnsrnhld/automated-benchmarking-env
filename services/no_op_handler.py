from .event_handler import EventHandler, JobRequestMessage, ResponseMessage, AppRequestMessage


class NoOpEventHandler(EventHandler):

    def __init__(self, db):
        pass

    def handle_job_start(self, message: JobRequestMessage) -> ResponseMessage:
        return self.no_op_recommendation(message)

    def handle_job_end(self, message: JobRequestMessage) -> ResponseMessage:
        return self.no_op_recommendation(message)

    def handle_application_start(self, message: AppRequestMessage) -> ResponseMessage:
        return self.no_op_recommendation(message)

    def handle_application_end(self, message: JobRequestMessage) -> ResponseMessage:
        return self.no_op_recommendation(message)
