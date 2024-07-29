import yaml
from jinja2 import Template
from typing import Dict, Any


class TemplateUtil:
    def __init__(self):
        pass

    @staticmethod
    def template(file_path: str, template_values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load a YAML file, apply Jinja2 templating with the provided values, and return the rendered YAML as a
        dictionary.

        :param file_path: Path to the YAML file.
        :param template_values: Dictionary of values for templating.
        :return: Dictionary representation of the rendered YAML.
        """
        # Load the YAML file content
        with open(file_path, 'r') as file:
            file_content = file.read()

        template = Template(file_content)
        rendered_content = template.render(template_values)

        yaml_dict = yaml.safe_load(rendered_content)

        return yaml_dict
