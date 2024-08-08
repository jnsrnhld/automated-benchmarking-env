import logging
import pymongo

from time import sleep
from hdfs import InsecureClient

from kopf_operator import Operator
from config import Config


def connect_to_mongodb():
    client = pymongo.MongoClient(Config.MONGODB_CONNECTION_STRING)
    db = client.get_database(Config.MONGODB_DATABASE)
    print(f"Connected to MongoDB! Listing collections: {db.list_collection_names()}")


def main():
    logging.basicConfig(level=logging.INFO)

    # Operator().start()  # operator works
    # connect_to_mongodb()  # mongodb connection works

    # HDFS works
    client = InsecureClient("http://34.32.17.185:32489")
    print(client.status("/"))

    while True:
        sleep(5)


if __name__ == '__main__':
    main()
