import argparse

from .enel_service.enel_event_handler import EnelEventHandler
from .server import ZeroMQServer
from .event_handler import EventHandler, NoOpEventHandler
from .ellis_port.ellis_event_handler import EllisEventHandler


def get_event_handler(handler_name: str) -> EventHandler:
    """
    Returns an instance of the event handler based on the handler name.

    :param handler_name: Name of the event handler class to instantiate.
    :param db: MongoDB database instance to pass to handlers.
    :return: An instance of EventHandler.
    """
    handler_classes = {
        'NoOpEventHandler': NoOpEventHandler,
        'EllisEventHandler': EllisEventHandler,
        'EnelEventHandler': EnelEventHandler,
        # 'OtherEventHandler': OtherEventHandler,
    }

    try:
        handler_class = handler_classes[handler_name]
        return handler_class()
    except KeyError:
        raise ValueError(f"Unknown event handler: {handler_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the bridge service")
    parser.add_argument(
        '--handler',
        type=str,
        default='NoOpEventHandler',
        help='Name of the event handler class to use (e.g., NoOpEventHandler)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5555,
        help='Port number to listen on (default: 5555)'
    )
    args = parser.parse_args()

    event_handler = get_event_handler(args.handler)
    server = ZeroMQServer(event_handler, args.port)
    server.start()
