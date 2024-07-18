#!/usr/bin/env bash
# adjust if necessary
gcloud config set project fog-computing-427208

# create VPC
gcloud compute networks create kubespray-cluster --subnet-mode custom

gcloud compute networks subnets create kubernetes-subnet \
--network kubespray-cluster \
--range 10.240.0.0/24 \
--region europe-west10

# firewall rules
gcloud compute firewall-rules create kubespray-cluster-allow-internal \
--allow tcp,udp,icmp \
--network kubespray-cluster \
--source-ranges 10.240.0.0/24

gcloud compute firewall-rules create kubespray-cluster-allow-external \
--allow tcp:80,tcp:6443,tcp:443,tcp:22,icmp \
--network kubespray-cluster \
--source-ranges 0.0.0.0/0

# create control planes
for i in 0 1; do # adjust amount of control planes if necessary
gcloud compute instances create controller-${i} \
--can-ip-forward \
--create-disk=auto-delete=yes,boot=yes,device-name=instance-20240718-210829,image=projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20240701,mode=rw,size=125,type=projects/fog-computing-427208/zones/us-central1-f/diskTypes/pd-balanced \
--machine-type e2-standard-2 \
--private-network-ip 10.240.0.1${i} \
--scopes compute-rw,storage-ro,service-management,service-control,logging-write,monitoring \
--subnet kubernetes-subnet \
--tags kubespray-cluster,controller \
--zone europe-west10-c
done

# create workers
for i in 0 1; do # adjust amount of workers if necessary
gcloud compute instances create worker-${i} \
--can-ip-forward \
--machine-type e2-standard-2 \
--create-disk=auto-delete=yes,boot=yes,device-name=instance-20240718-210829,image=projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20240701,mode=rw,size=125,type=projects/fog-computing-427208/zones/us-central1-f/diskTypes/pd-balanced \
--private-network-ip 10.240.0.2${i} \
--scopes compute-rw,storage-ro,service-management,service-control,logging-write,monitoring \
--subnet kubernetes-subnet \
--tags kubespray-cluster,worker \
--zone europe-west10-c
done

# list instances
gcloud compute instances list --filter="tags.items=kubespray-cluster"
