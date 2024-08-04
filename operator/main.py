import logging
import pymongo

from time import sleep
from hdfs import InsecureClient
client = InsecureClient("http://localhost:9870")
# also specifying the user=stackable does not help
# client = InsecureClient("http://localhost:9870", user="stackable")
print(client.status("/"))

from kopf_operator import Operator
from config import Config


def connect_to_mongodb():
    client = pymongo.MongoClient(Config.MONGODB_CONNECTION_STRING)
    db = client.get_database(Config.MONGODB_DATABASE)
    print(f"Connected! Collections: {db.list_collection_names()}")


def main():
    logging.basicConfig(level=logging.INFO)

    # Operator().start()  # operator works
    # connect_to_mongodb()  # mongodb connection works

    client = InsecureClient("http://hdfs-cluster-namenode-default-0.hdfs-cluster-namenode-default.default.svc.cluster.local:9870")
    print(client.status("/"))

    # while True:
    #     sleep(5)


if __name__ == '__main__':
    main()
