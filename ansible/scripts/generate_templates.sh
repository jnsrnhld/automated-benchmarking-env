#!/usr/bin/env bash
script=$1 # The run-command.sh script to run
ansible_values_file=$2 # Path to the YAML file containing additional template values
template_path=$3 # Path to the Jinja2 template file
output_path=$(dirname $script) # Path where the rendered file will be saved

main_class_with_arguments=$(bash "$script")
python3 sparkapp-templater.py "$main_class_with_arguments" "$ansible_values_file" "$template_path" "$output_path"
