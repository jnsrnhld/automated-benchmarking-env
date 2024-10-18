# Setup

## Prerequisites

## Install python dependencies

```bash
# setup virtual environment
python3 -m venv ansible_venv
source ansible_venv/bin/activate
# or just install dependencies for ansible
pip install -r ansible/requirements.txt
```

### k8s cluster

For information on how to set up a `k8s` cluster via `kubespray`, see [k8s setup](k8s_setup/README.md).
All the following commands are expected to be executed from project root directory if not stated otherwise.

### Spark image

Because HiBench does not support Spark versions later than 3.1.1 and there are no public available images of this 
version which work with the kubeflow spark-operator (as of late 2024), you may provide a spark image with the desired 
version and set its name in the ansible [vars](vars.yaml) file.

Therefore, follow these step after cloning the [spark repository](https://github.com/apache/spark) and creating a 
docker repository on dockerhub:
```bash
# checkout to the target version, e.g. 3.1.1
git checkout "v.3.1.1"
# build Spark with k8s support
./build/mvn -Pkubernetes -DskipTests clean package
# login to your docker repo
docker logout && docker login -u=$YOUR_DOCKERHUB_USERNAME
# build the image
bin/docker-image-tool.sh -r $YOUR_DOCKERHUB_USERNAME -t $VERSION_TAG build
# push the image
bin/docker-image-tool.sh -r $YOUR_DOCKERHUB_USERNAME -t $VERSION_TAG push
```

## Software stack deployment using ansible

##### Adjust cloud inventory

[The cloud inventory](cloud.yaml) defines the setup for cloud machines:
- `remote` should contain all available remote machines.
- `leader` should contain a machine which is used to execute kubectl/helm commands, runs the bridge service, 
scaling services, database, etc.
- `worker` are all machines that could be part of the hdfs cluster and/or contribute as workers to the batch processing 
framework

##### Run playbooks from root dir

```shell
# Run playbook with cloud inventory: 
ansible-playbook ansible/playbooks/setup.yaml --ask-become-pass
```

###### Playbooks 

| name    | content                                                                                                                                                                                                                                                                                                                                                                         |
|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| setup   | Set's up the required software stack for the experiments.                                                                                                                                                                                                                                                                                                                       |
| facts   | Gathers all facts necessary for development. Therefor, the local `/etc/hosts` file has to be modified to make service names resolvable on your local machine. This requires a sudo password for the user you execute the playbook with. By passing `--ask-become-pass` when running the playbook, you are required to provide this password. Otherwise, the playbook will fail. |
| cleanup | Reverts the changes to remote machines and k8s cluster made by the setup script as far as possbible.                                                                                                                                                                                                                                                                            |
| hibench | Run HiBench benchmarks.                                                                                                                                                                                                                                                                                                                                                         |
