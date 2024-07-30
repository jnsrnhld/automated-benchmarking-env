import asyncio
import logging
import threading
import kopf


class Operator:
    def __init__(self):
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self.kopf_thread)
        self._thread.start()

    @staticmethod
    def kopf_thread():
        asyncio.run(kopf.operator(
            clusterwide=True,
            standalone=True,
        ))

    @staticmethod
    @kopf.on.login()
    def login_fn(**kwargs):
        return kopf.login_with_kubeconfig(**kwargs)

    @staticmethod
    @kopf.on.create('SparkApplication')
    def create_fn(body, **kwargs):
        logging.info(f"Spark application {body.metadata.name} created")

    @staticmethod
    @kopf.on.event('SparkApplication')
    def my_handler(event, **_):
        body = event['object']
        logging.info(f"Spark application {body['metadata']['name']} updated [{event['type']}]:"
                     f"State => {body['status']['applicationState']['state']} | "
                     f"Execution attempts => {body['status']['executionAttempts']}")
