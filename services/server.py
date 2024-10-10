import zmq

from event_handler import EventHandler, EventType, RequestMessage, ResponseMessage


class ZeroMQServer:
    """
    ZeroMQ server that receives RequestMessages from clients and responds with ResponseMessages.
    """

    def __init__(self, event_handler: EventHandler, port=5555):
        self.port = port
        self.event_handler = event_handler
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{self.port}")

    def start(self):
        print(f"Server started at tcp://*:{self.port}")
        try:
            while True:
                message = self.socket.recv_string()
                request_message = RequestMessage.from_json(message)

                response_message = self.process_message(request_message)
                response_json = response_message.to_json()
                self.socket.send_string(response_json)

        except KeyboardInterrupt:
            print("Server shutting down.")
        finally:
            self.socket.close()
            self.context.term()

    def process_message(self, message: RequestMessage) -> ResponseMessage:
        """
        Process the incoming request and delegate to the appropriate event handler method.
        """
        event_type = message.event_type
        print(f"Processing {event_type.value} event for app_id: {message.app_id}")

        if event_type == EventType.JOB_START:
            return self.event_handler.handle_job_start(message)
        elif event_type == EventType.JOB_END:
            return self.event_handler.handle_job_end(message)
        elif event_type == EventType.APPLICATION_END:
            return self.event_handler.handle_application_end(message)
        else:
            print(f"Unknown event type: {event_type}")
            raise ValueError(f"Unknown event type: {event_type}")
