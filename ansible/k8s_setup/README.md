##### Deploy k8s cluster via kubespray

```shell
# setup kubespray from within ansible dir
git clone git@github.com:kubernetes-sigs/kubespray.git --branch "v2.25.0"
cd kubespray
pip install -U -r requirements.txt
```
Then follow EXACTLY! the steps described [here](https://github.com/kubernetes-sigs/kubespray/blob/master/docs/getting_started/setting-up-your-first-cluster.md#set-up-kubespray).

Further, adjust the following `group_vars` in the corresponding inventory you created:
- Set a `kube_version`, e.g. to `v1.27.5`
- Set `kubeconfig_localhost` to `true`
- Add at least 1 public IP address of your machines `supplementary_addresses_in_ssl_keys`: See
[this section](https://github.com/kubernetes-sigs/kubespray/blob/master/docs/getting_started/setting-up-your-first-cluster.md#set-up-kubespray)
to understand how to access the cluster from your local machine.
- Set `metrics_server_enabled` to true
- Set `local_volume_provisioner_enabled` to true

Command to set `KUBECONFIG` temporarily: `export KUBECONFIG=/$PWD/inventory/mycluster/artifacts/admin.conf`.
You have to adjust the IP to one of the public IP addresses you passed to `supplementary_addresses_in_ssl_keys`.

###### Start/Reset the cluster

```shell
# reset a running cluster
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES # only if run on macOS https://github.com/rails/rails/issues/38560 
ansible-playbook -i inventory/mycluster/hosts.yaml --become --become-user=root reset.yml
# create a new cluster
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES # only if run on macOS https://github.com/rails/rails/issues/38560
ansible-playbook -i inventory/mycluster/hosts.yaml  --become --become-user=root cluster.yml
```

###### Access cluster from local machine

```shell
# points to the admin.conf file generated automatically
export KUBECONFIG=/$PWD/inventory/mycluster/artifacts/admin.conf
```
