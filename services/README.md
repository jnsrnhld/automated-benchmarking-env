## Start bridge service

## Install python dependencies 

The dependencies require python version >=3.10. Make sure to upgrade build dependencies before installing:
`pip install --upgrade pip setuptools wheel`

```bash
# setup virtual environment 
python -m venv services_venv
source services_venv/bin/activate
# or just install dependencies for ansible
pip install -r services/requirements.txt
```

```bash
# uses a NoOp Handler and port 5555 by default
python3 -m services.bridge_service
# you may want to overwrite defaults
python3 -m services.bridge_service --handler YourEventHandler --port 1234
# use Ellis handler
python3 -m services.bridge_service --handler EllisEventHandler 
# use ENEL handler (adjust values according to your needs or run ansible/playbook/facts.yaml to gather values)
MONGODB_ENDPOINT="mongodb-0.mongodb-headless.default.svc.cluster.local" \
MONGODB_CONNECTION_PARAMS="replicaSet=rs0&authSource=test" \
MONGODB_DATABASE="test" \
MONGODB_USERNAME="test" \
MONGODB_PASSWORD="Password1!" \
HDFS_ENDPOINT="http://localhost:9870" \
python3 -m services.bridge_service --handler EnelEventHandler 
```
