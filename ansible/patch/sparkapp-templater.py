import re
import yaml
from jinja2 import Environment, FileSystemLoader
from pathlib import Path


def parse_input_string(input_string: str) -> dict:
    """
    Parse the input string to extract the main class and arguments.

    Args:
        input_string (str): Input string containing the main class and arguments.

    Returns:
        dict: Dictionary with `main_class` and `arguments` keys.
    """

    # the prepare.sh script might echo other stuff that we discard
    # all test apps are part of hibench or spark package
    trimmed = re.search(r'(com\.intel\.hibench|org\.apache\.spark).*', input_string).group(0)

    parts = trimmed.split()
    main_class = parts[0]
    name = main_class.split('.')[-1].lower()  # main class without package info
    arguments = parts[1:]
    return {
        "name": name,
        "hibench_main_class": main_class,
        "arguments": arguments
    }


def render_template(template_path: str, context: dict, output_path: str) -> None:
    """
    Render the Jinja2 template with the provided context and write the output to a file.

    Args:
        template_path (str): Path to the Jinja2 template file.
        context (dict): Dictionary with the values to be used in the template.
        output_path (str): Path where the rendered file will be saved.
    """
    env = Environment(loader=FileSystemLoader(Path(template_path).parent))
    template = env.get_template(Path(template_path).name)
    output = template.render(context)

    with open(output_path, 'w') as output_file:
        output_file.write(output)


def main(input_string: str, config_path: str, template_path: str, output_path: str) -> None:
    """
    Main function to generate the templated YAML file.

    Args:
        input_string (str): The input string with the Java class and arguments.
        config_path (str): Path to the YAML file containing additional template values.
        template_path (str): Path to the Jinja2 template file.
        output_path (str): Path where the rendered file will be saved.
    """
    # Parse the input string to extract the main class and arguments
    parsed_data = parse_input_string(input_string)

    # Load the config file containing the additional template values
    with open(config_path, 'r') as config_file:
        config_data = yaml.safe_load(config_file)

    # Merge the parsed data with the config data
    context = {**config_data, **parsed_data}

    # Render the template and save the output
    render_template(template_path, context, output_path)


if __name__ == "__main__":
    import argparse

    # Setup command line arguments
    parser = argparse.ArgumentParser(description="Generate templated YAML using Jinja2.")
    parser.add_argument("input_string", type=str, help="The input string containing the Java class and arguments.")
    parser.add_argument("config_path", type=str, help="Path to the YAML file containing additional template values.")
    parser.add_argument("template_path", type=str, help="Path to the Jinja2 template file.")
    parser.add_argument("output_path", type=str, help="Path where the rendered file will be saved.")

    args = parser.parse_args()

    # Call the main function with the provided arguments
    main(args.input_string, args.config_path, args.template_path, args.output_path)
