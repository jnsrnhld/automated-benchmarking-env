# Notes
- linux-based systems are required
- versions must be fixed for reproducibility (if vendors do not delete older versions)
- Ansible triggered from local machine and run in virtual env
- after installing Ansible, restart terminal
- Ansible "present" state desired when installing dependencies
- Ansible action should be atomic if possible
- for simplicity, we assume all nodes require Java for Spark or HDFS
- k8s cluster setup with kubespray
