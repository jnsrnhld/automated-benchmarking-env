# Setup

## Install python dependencies

```bash
# setup virtual environment
python3 -m venv venv
source venv/bin/activate
# install all requirements
find . -maxdepth 2 -name 'requirements.txt' -exec pip install -r {} \;
```

# Start bridge service

```bash
python3 -m services.bridge_service
# you may want to overwrite defaults
python3 -m services.bridge_service --handler EllisEventHandler --port 1234
```
