# Setup

## Install python dependencies

```bash
# setup virtual environment
python3 -m venv venv
source venv/bin/activate
# install all requirements for ansible and services
find . -maxdepth 2 -name 'requirements.txt' -exec pip install -r {} \;
# or just install dependencies for ansible
pip install -r ansible/requirements.txt
```

## Software stack setup

For information on how to set up the whole software stack, follow [this guide](ansible/README.md).

## Start bridge service

```bash
python3 -m services.bridge_service
# you may want to overwrite defaults
python3 -m services.bridge_service --handler EllisEventHandler --port 1234
```
