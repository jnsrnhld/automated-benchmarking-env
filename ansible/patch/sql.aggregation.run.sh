#!/bin/bash
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

current_dir=`dirname "$0"`
current_dir=`cd "$current_dir"; pwd`
root_dir=${current_dir}/../../../../../
workload_config=${root_dir}/conf/workloads/sql/aggregation.conf
. "${root_dir}/bin/functions/load_bench_config.sh"

enter_bench ScalaSparkAggregation ${workload_config} ${current_dir}
show_bannar start

# prepare SQL
### PATCH START ###
SQL_FILE="uservisits_aggre.hive"
HIVEBENCH_SQL_FILE="${WORKLOAD_RESULT_FOLDER}/${SQL_FILE}"
HIVEBENCH_REMOTE_SQL_FILE="${INPUT_HDFS}/${SQL_FILE}";
prepare_sql_aggregation ${HIVEBENCH_SQL_FILE} ${HIVEBENCH_REMOTE_SQL_FILE}

START_TIME=`timestamp`
rmr_hdfs $OUTPUT_HDFS
run_spark_job com.intel.hibench.sparkbench.sql.ScalaSparkSQLBench ScalaAggregation ${HIVEBENCH_REMOTE_SQL_FILE}
END_TIME=`timestamp
### PATCH END ###`

sleep 5
SIZE=`dir_size $OUTPUT_HDFS`
gen_report ${START_TIME} ${END_TIME} ${SIZE:-0}
show_bannar finish
leave_bench