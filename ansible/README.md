# Ansible hints

For information on how to set up a `k8s` cluster via `kubespray`, see [k8s setup](k8s_setup/README.md).

##### Prepare local python venv
```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

##### Adjust cloud inventory

[The cloud inventory](cloud.yaml) defines the setup for cloud machines:
- `remote` should contain all available remote machines.
- `leader` should contain a machine which is used to execute kubectl/helm commands, runs the bridge service, 
scaling services, database, etc.
- `worker` are all machines that will be part of the hdfs cluster and/or contribute as workers to the batch processing 
framework

##### Run playbooks from root dir 

```shell
# Run playbook with cloud inventory (default): 
ansible-playbook ansible/playbooks/setup.yaml
# Run playbook with local inventory:
ansible-playbook ansible/playbooks.yaml -i ansible/local.yaml
```

###### Playbooks 

| name   | content                                                                                               |
|--------|-------------------------------------------------------------------------------------------------------|
| setup  | Set's up the required software stack for the experiments.                                             |
| verify | Verifies the setup did work properly by submitting a spark application and on/offloading date to HDFS |
