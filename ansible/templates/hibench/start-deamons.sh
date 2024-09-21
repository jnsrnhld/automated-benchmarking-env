#!/usr/bin/env bash
# ansible is not sourcing .bashrc
export JAVA_HOME=$(readlink -f $(which java) | sed "s:bin/java::")
export PATH=$JAVA_HOME/bin:$PATH
export PDSH_RCMD_TYPE=ssh

# hdfs
hdfs_address={{ hdfs_address }}
# only run if HDFS is running locally (and not in k8s cluster)
if [[ $hdfs_address == *"localhost"* ]]; then
  sudo rm -rf /tmp/hadoop-{{ linux_username }}/*
  yes | {{ hadoop_dir }}/bin/hdfs namenode -format
  {{ hadoop_dir }}/sbin/start-dfs.sh
fi

# yarn
{{ hadoop_dir }}/sbin/stop-yarn.sh
{{ hadoop_dir }}/sbin/start-yarn.sh
