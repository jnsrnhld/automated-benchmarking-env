# Local deployment

## Prerequisites:
The following CLI tools are required:
- `kind`
- `helmfile`

```shell
# Create kind cluster
kind create cluster --name enel-experiments
# From enel-experiments root dir, deploy the stack (metrics server, HDFS, Spark, MongoDB)
# We need the `set` magic to make the `.env` content available for `helmfile`
set -a; source .env; set +a; helmfile apply --file deployment/helmfile.yaml
```
