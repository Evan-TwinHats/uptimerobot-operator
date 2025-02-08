"""Contains functions for creating V1JSONSchemaProps of different types."""
from kubernetes.client import V1JSONSchemaProps


def v1string(description, enum_type=None, property_type='string'):
    """Create a V1JSONSchemaProps of type 'string'
    Optionally sets allowed values and updates the description
    based on an Enum if provided"""
    enum = (None if enum_type is None
            else list(enum_type.__members__.keys()))
    description = (description if enum_type is None
                   else f"{description}, one of: {','.join(list(enum_type.__members__.keys()))}")
    return V1JSONSchemaProps(
        type=property_type,
        enum=enum,
        description=description
    )


def v1object(description):
    """Create a V1JSONSchemaProps of type 'object'"""
    return V1JSONSchemaProps(
        type='object',
        description=description,
        x_kubernetes_preserve_unknown_fields=True
    )


def schema_props(props, required=None, preserve_unknown_fields=None):
    """Create a V1JSONSchemaProps of type 'object' 
    that defines V1JSONSchemaProps to be used in a CRD"""
    return V1JSONSchemaProps(
        type='object',
        properties=props,
        required=required,
        x_kubernetes_preserve_unknown_fields=preserve_unknown_fields
    )


def v1integer(description, mult=1.):
    """Create a V1JSONSchemaProps of type 'integer' 
    with optional multiplier for allowed values"""
    return V1JSONSchemaProps(
        type='integer',
        multiple_of=mult,
        description=description
    )


def v1boolean(description):
    """Create a V1JSONSchemaProps of type 'boolean'"""
    return v1string(description, property_type='boolean')


def v1number(description):
    """Create a V1JSONSchemaProps of type 'boolean'"""
    return v1string(description, property_type='number')
