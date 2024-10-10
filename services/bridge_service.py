import argparse
from server import ZeroMQServer

from event_handler import EventHandler
from no_op_handler import NoOpEventHandler


def get_event_handler(handler_name: str) -> EventHandler:
    """
    Returns an instance of the event handler based on the handler name.
    """
    handler_classes = {
        'NoOpEventHandler': NoOpEventHandler,
        # 'OtherEventHandler': OtherEventHandler,
    }

    try:
        handler_class = handler_classes[handler_name]
        return handler_class()
    except KeyError:
        raise ValueError(f"Unknown event handler: {handler_name}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Start the bridge service with a specified event handler.")
    parser.add_argument(
        '--handler',
        type=str,
        default='NoOpEventHandler',
        help='Name of the event handler class to use (e.g., NoOpEventHandler)'
    )
    args = parser.parse_args()

    event_handler = get_event_handler(args.handler)
    server = ZeroMQServer(event_handler)
    server.start()
