import os
import logging
from time import sleep

from kubernetes import config
from kopf_operator import Operator

def main():
    logging.basicConfig(level=logging.INFO)

    ensureKubeconfigIsPresent()
    Operator().start()

    while True:
        sleep(5)

    # try:
    # verify we can interact with spark operator
    # spark_app = TemplateUtil.template(f"{os.getcwd()}/ansible/charts/spark-pi.yaml", {'spark_version': '3.5.0'})
    #
    # extensions_api = client.ApiextensionsV1Api()
    # api_response = extensions_api.create_custom_resource_definition(spark_app)
    # logging.info(api_response)

    # client = pymongo.MongoClient("localhost", 27017)

    # except KeyboardInterrupt:
    #     print("Stopping the scheduler...")


def ensureKubeconfigIsPresent():
    kubeconfig_path = os.getenv('KUBECONFIG')
    if not kubeconfig_path:
        raise ValueError("KUBECONFIG environment variable is not set")
    config.load_kube_config()


if __name__ == '__main__':
    main()
