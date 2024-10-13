import argparse
import pymongo

from pymongo.database import Database
from .config import Config
from .server import ZeroMQServer
from .event_handler import EventHandler, NoOpEventHandler
from .ellis_port.ellis_event_handler import EllisEventHandler


def connect_to_mongodb():
    try:
        client = pymongo.MongoClient(Config.MONGODB_CONNECTION_STRING, tz_aware=True)
        db = client[Config.MONGODB_DATABASE]
        print(f"Connected to MongoDB database: {Config.MONGODB_DATABASE}")
        return db
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise


def get_event_handler(handler_name: str, db: Database) -> EventHandler:
    """
    Returns an instance of the event handler based on the handler name.

    :param handler_name: Name of the event handler class to instantiate.
    :param db: MongoDB database instance to pass to handlers.
    :return: An instance of EventHandler.
    """
    handler_classes = {
        'NoOpEventHandler': NoOpEventHandler,
        'EllisEventHandler': EllisEventHandler,
        # 'OtherEventHandler': OtherEventHandler,
    }

    try:
        handler_class = handler_classes[handler_name]
        return handler_class(db)
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

    mongodb = connect_to_mongodb()
    event_handler = get_event_handler(args.handler, mongodb)
    server = ZeroMQServer(event_handler, args.port)
    server.start()
