import os
import asyncio
import threading
import logging
import kopf

from kubernetes import client
from template_util import TemplateUtil


@kopf.on.create('SparkApplication')
def pod_spec_handler(name, logger):
    logger.info(f"Spark application {name} running")


@kopf.on.update('SparkApplication')
def pod_spec_handler(name, status, logger):
    logger.info(f"Spark application {name} updated. Current Status is: {status}")


def kopf_thread():
    asyncio.run(kopf.operator())


def main():
    logging.basicConfig(level=logging.INFO)
    os.environ["KUBECONFIG"] = f"{os.getcwd()}/ansible/k8s_setup/kubespray/inventory/mycluster/artifacts/admin.conf"

    operator = threading.Thread(target=kopf_thread)
    operator.start()

    try:
        # verify we can interact with spark operator
        spark_app = TemplateUtil.template("ansible/charts/spark-pi.yaml", {'spark_version': '3.5.0'})

        extensions_api = client.ApiextensionsV1Api()
        api_response = extensions_api.create_custom_resource_definition(spark_app)
        logging.info(api_response)

    except KeyboardInterrupt:
        print("Stopping the scheduler...")
