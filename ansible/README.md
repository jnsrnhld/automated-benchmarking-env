# Ansible hints

For information on how to set up a `k8s` cluster via `kubespray`, see [k8s setup](k8s_setup/README.md).

##### Prepare local python venv
```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

##### Run playbooks from root dir 

```shell
# Run playbook with cloud inventory (default): 
ansible-playbook ansible/site.yaml
# Run playbook with local inventory:
ansible-playbook ansible/site.yaml -i ansible/local.yaml
```
