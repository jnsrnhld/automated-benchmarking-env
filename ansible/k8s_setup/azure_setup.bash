#!/usr/bin/env bash

# variables - adjust as needed
RESOURCE_GROUP="Arnhold_MasterThesis"
VNET_NAME="kubespray-vnet"
SUBNET_NAME="kubernetes-subnet"
SUBNET_CIDR="10.240.0.0/24"
NSG_NAME="kubespray-nsg"
VM_SIZE="Standard_E8s_v5"
DISK_SIZE_GB="1024"
IMAGE="Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest"
TAGS="kubernetes-the-kubespray-way"
SSH_PUBLIC_KEY="$HOME/.ssh/id_rsa.pub"

# Create virtual network and subnet
az network vnet create \
  --resource-group $RESOURCE_GROUP \
  --name $VNET_NAME \
  --address-prefix "10.240.0.0/16" \
  --subnet-name $SUBNET_NAME \
  --subnet-prefix $SUBNET_CIDR

# Create network security group and rules
az network nsg create \
  --resource-group $RESOURCE_GROUP \
  --name $NSG_NAME

# Allow internal traffic
az network nsg rule create \
  --resource-group $RESOURCE_GROUP \
  --nsg-name $NSG_NAME \
  --name AllowInternal \
  --priority 1000 \
  --access Allow \
  --protocol "*" \
  --direction Inbound \
  --source-address-prefixes $SUBNET_CIDR \
  --source-port-ranges "*" \
  --destination-address-prefixes "*" \
  --destination-port-ranges "*"

# Allow external traffic for required ports
az network nsg rule create \
  --resource-group $RESOURCE_GROUP \
  --nsg-name $NSG_NAME \
  --name AllowExternal \
  --priority 2000 \
  --access Allow \
  --protocol Tcp \
  --direction Inbound \
  --source-address-prefixes "0.0.0.0/0" \
  --destination-port-ranges 22 80 443 6443

# Associate NSG to subnet
az network vnet subnet update \
  --resource-group $RESOURCE_GROUP \
  --vnet-name $VNET_NAME \
  --name $SUBNET_NAME \
  --network-security-group $NSG_NAME

# Create control plane VMs
for i in {0..0}; do
  az vm create \
    --resource-group $RESOURCE_GROUP \
    --name controller-$i \
    --size $VM_SIZE \
    --image $IMAGE \
    --admin-username "$(whoami)" \
    --ssh-key-value $SSH_PUBLIC_KEY \
    --vnet-name $VNET_NAME \
    --subnet $SUBNET_NAME \
    --private-ip-address 10.240.0.1${i} \
    --nsg $NSG_NAME \
    --tags $TAGS \
    --os-disk-size-gb $DISK_SIZE_GB
done

# Create worker VMs
for i in {0..4}; do
  az vm create \
    --resource-group $RESOURCE_GROUP \
    --name worker-$i \
    --size $VM_SIZE \
    --image $IMAGE \
    --admin-username "$(whoami)" \
    --ssh-key-value $SSH_PUBLIC_KEY \
    --vnet-name $VNET_NAME \
    --subnet $SUBNET_NAME \
    --private-ip-address 10.240.0.2${i} \
    --nsg $NSG_NAME \
    --tags $TAGS \
    --os-disk-size-gb $DISK_SIZE_GB
done

# List instances with tags
az vm list --resource-group $RESOURCE_GROUP --query "[?tags.kubernetes-the-kubespray-way]" -o table
