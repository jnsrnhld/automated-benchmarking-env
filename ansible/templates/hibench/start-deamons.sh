#!/usr/bin/env bash
# ansible is not sourcing .bashrc
export JAVA_HOME=$(readlink -f $(which java) | sed "s:bin/java::")
export PATH=$JAVA_HOME/bin:$PATH
export PDSH_RCMD_TYPE=exec

# stop services which might are already running
{{ hadoop_dir }}/sbin/stop-all.sh

# hadoop
sudo rm -rf /tmp/hadoop-{{ linux_username }}/*
yes | {{ hadoop_dir }}/bin/hdfs namenode -format
{{ hadoop_dir }}/sbin/start-dfs.sh
{{ hadoop_dir }}/bin/hdfs dfs -mkdir /user
{{ hadoop_dir }}/bin/hdfs dfs -mkdir /user/{{ linux_username }}

# yarn
{{ hadoop_dir }}/sbin/start-yarn.sh
