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
- `worker` are all machines that could be part of the hdfs cluster and/or contribute as workers to the batch processing 
framework

##### HDFS setup
HDFS is operated by a [`stackable` operator](https://docs.stackable.tech/home/stable/hdfs/). It will create multiple 
[`PersistentVolumeClaim`](https://kubernetes.io/docs/concepts/storage/persistent-volumes)s, therefore it expects a 
mapping to some [`StorageClass`](https://kubernetes.io/docs/concepts/storage/storage-classes/). If you create the k8s 
cluster as described here => [`k8s setup`](k8s_setup/README.md), everything will be auto-wired.
Per default, the [Local Persistence Volume Static Provisioner](https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner)
will be used and persistent volumes are automatically created and provisioned.

Otherwise, you need to adjust the `hdfs_storage_class` variable [here](vars.yaml). Set it to the name of the 
`StorageClass` the can provision storage for HDFS.

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
