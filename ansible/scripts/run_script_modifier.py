import sys

import sys
import os


def modify_script(input_file: str, output_file: str) -> None:
    """
    Modify the given script file by deleting specific lines and modifying others.

    This function reads a shell script from an input file, performs the following tasks:
    - Deletes lines containing specific commands.
    - Replaces "run_spark_job" with "echo" in the corresponding line.

    The modified script is then saved to an output file.

    Args:
        input_file (str): The path to the input shell script file.
        output_file (str): The path where the modified script should be saved.

    Returns:
        None
    """
    delete_lines = [
        "START_TIME=`timestamp`",
        "show_bannar start",
        "SIZE=`dir_size $INPUT_HDFS`",
        "END_TIME=`timestamp`",
        "gen_report ${START_TIME} ${END_TIME} ${SIZE}",
        "show_bannar finish",
        "leave_bench"
    ]

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            stripped_line = line.strip()

            if stripped_line in delete_lines:
                continue

            if stripped_line.startswith("run_spark_job"):
                line = line.replace("run_spark_job", "echo")

            outfile.write(line)


def find_and_modify_run_sh_files(base_dir: str) -> None:
    """
    Search for 'run.sh' files recursively in the given directory, modify them, and save them with a new name.

    This function searches for files named 'run.sh' within the provided directory and its subdirectories. For each
    found file, it applies the `modify_script` function to modify the file and saves the result with a new name based
    on the directory in which the original file was found.

    Args:
        base_dir (str): The path to the base directory where the search should begin.

    Returns:
        None
    """
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file == "run.sh":
                input_file = os.path.join(root, file)

                output_file_name = "run-command.sh"
                output_file = os.path.join(root, output_file_name)

                modify_script(input_file, output_file)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python modify_script.py <base_directory>")
        sys.exit(1)

    base_dir = sys.argv[1]

    find_and_modify_run_sh_files(base_dir)
