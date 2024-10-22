import zmq

from .event_handler import EventHandler, EventType, ResponseMessage, MessageEnvelope, \
    AppStartMessage, AppEndMessage, JobStartMessage, JobEndMessage


class ZeroMQServer:
    """
    ZeroMQ server that receives RequestMessages from clients and responds with ResponseMessages.
    """

    def __init__(self, event_handler: EventHandler, port: int):
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
                envelope = MessageEnvelope.from_json(message)

                response_message = self.process_message(envelope)
                response_json = response_message.json()
                self.socket.send_string(response_json)

        except KeyboardInterrupt:
            print("Server shutting down.")
        finally:
            self.socket.close()
            self.context.term()

    def process_message(self, envelope: MessageEnvelope) -> ResponseMessage:
        """
        Process the incoming request and delegate to the appropriate event handler method.
        """
        event_type = envelope.event_type
        print(f"Processing {event_type.value} event")

        if event_type == EventType.JOB_START:
            message = JobStartMessage.create(envelope.payload)
            return self.event_handler.handle_job_start(message)
        elif event_type == EventType.JOB_END:
            message = JobEndMessage.create(envelope.payload)
            return self.event_handler.handle_job_end(message)
        elif event_type == EventType.APPLICATION_START:
            message = AppStartMessage.create(envelope.payload)
            return self.event_handler.handle_application_start(message)
        elif event_type == EventType.APPLICATION_END:
            message = AppEndMessage.create(envelope.payload)
            return self.event_handler.handle_application_end(message)
        else:
            print(f"Unknown event type: {event_type}")
            raise ValueError(f"Unknown event type: {event_type}")
