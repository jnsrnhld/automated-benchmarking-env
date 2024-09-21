#!/usr/bin/env bash
script=$INPUT_PATH
main_class_with_arguments=$(bash "$script")
python3 sparkapp-templater.py "$main_class_with_arguments" "$1" "$2" "$3"
