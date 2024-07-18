# Ansible hints

##### Prepare local python venv
```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

##### Deploy k8s cluster via kubespray (optional)

```shell
# setup kubespray from within ansible dir
git clone git@github.com:kubernetes-sigs/kubespray.git --branch "v2.25.0"
cd kubespray
pip install -U -r requirements.txt
# copy sample inventory file and adjust according to your cluster
# see https://github.com/kubernetes-sigs/kubespray/blob/master/docs/ansible/ansible.md#inventory
cp -rfp inventory/sample inventory/cluster
# update ansible inventory file with inventory builder (add all you machine IPs like below)
# in the hosts.yaml, also update the ip to the respective local VPC IP and remove the access_ip.
CONFIG_FILE=inventory/cluster/hosts.yaml python3 contrib/inventory_builder/inventory.py ${IPS[@]}
declare -a IPS=(34.32.19.144 34.32.61.19)
# reset a running cluster
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES # only if run on macOS https://github.com/rails/rails/issues/38560 
ansible-playbook -i inventory/cluster/hosts.yaml --become --become-user=root reset.yml
# create a new cluster
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES # only if run on macOS https://github.com/rails/rails/issues/38560
ansible-playbook -i inventory/cluster/hosts.yaml  --become --become-user=root cluster.yml
```

##### Run playbooks from root dir 

```shell
# Run playbook with cloud inventory (default): 
ansible-playbook ansible/site.yaml
# Run playbook with local inventory:
ansible-playbook ansible/site.yaml -i ansible/local.yaml
```
