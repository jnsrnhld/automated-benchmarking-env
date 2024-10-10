# Setup

## Install python dependencies

```bash
# setup virtual environment
python3 -m venv venv
source venv/bin/activate
# install all requirements
find . -maxdepth 2 -name 'requirements.txt' -exec pip install -r {} \;
```
