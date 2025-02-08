"""Additional utility functions"""
import re
from kubernetes.client import V1CustomResourceColumnDefinition

pattern = re.compile(r'(?<!^)(?=[A-Z])')


def camel_to_snake_case(string):
    """Convert camel case to snake case"""
    return pattern.sub('_', string).lower()


def printer_column(name, path):
    """Create a V1CustomResourceColumnDefinitionto be used as a printer column"""
    return V1CustomResourceColumnDefinition(
        description=name,
        json_path=path,
        name=name,
        type='string'
    )
