"""Base class for CRDs. Also contains make_spec() for creating a CRD's spec"""
from abc import ABC, abstractmethod
from kubernetes.client import V1JSONSchemaProps, V1CustomResourceDefinitionSpec as CRD
from kubernetes.client import V1CustomResourceDefinitionVersion as Version
from kubernetes.client import V1CustomResourceValidation as CRDValidation
from kubernetes.client import V1CustomResourceDefinitionNames as Names
from kubernetes.client import V1CustomResourceColumnDefinition
from .property_types import v1object, schema_props  # pylint: disable=relative-beyond-top-level
GROUP = 'uptimerobot.twinhats.com'


class BaseCrd(ABC):
    """The base class for CRDs."""
    @staticmethod
    def version() -> str:
        """Retrieve the version for this CRD, or the default of v1beta1 if not overridden"""
        return 'v1beta1'

    @staticmethod
    def group() -> str:
        """Retrieve the group for this CRD, or uptimerobot.twinhats.com if not overridden"""
        return GROUP

    @staticmethod
    @abstractmethod
    def plural() -> str:
        """Retrieve the plural name for this CRD. Must be overridden in the child class."""

    @staticmethod
    @abstractmethod
    def singular() -> str:
        """Retrieve the singular name for this CRD. Must be overridden in the child class."""

    @staticmethod
    @abstractmethod
    def kind() -> str:
        """Retrieve the kind for this CRD. Must be overridden in the child class."""

    @staticmethod
    @abstractmethod
    def short_names() -> list[str]:
        """Retrieve the list of short names for this CRD. Must be overridden in the child class."""

    @staticmethod
    @abstractmethod
    def properties() -> dict[str, V1JSONSchemaProps]:
        """Retrieve the properties for this CRD as a dict[str, V1JsonSchemaProps]. 
        Must be overridden in the child class."""

    @staticmethod
    @abstractmethod
    def required_properties() -> list[str]:
        """Retrieve the list of property names that are required for this CRD. 
        Must be overridden in the child class."""

    @staticmethod
    def printer_columns() -> list[V1CustomResourceColumnDefinition]:
        """Retrieve the list of printer columns (fields to be displayed in tables) for this CRD. 
        Must be overridden in the child class."""
        return []

    @staticmethod
    @abstractmethod
    def spec_to_request_dict(name: str, spec: dict) -> dict:
        """Convert a spec dict to an UptimeRobot api request dict.
        Must be overridden in the child class."""


def make_spec(crd: type[BaseCrd]):
    """Create the spec for a given CRD class"""
    version = Version(name=crd.version(),
                      served=True,
                      storage=True,
                      schema=CRDValidation(schema_props(
                          {
                              'spec': schema_props(crd.properties(), crd.required_properties()),
                              'status': v1object(None)
                          })),
                      additional_printer_columns=crd.printer_columns())

    names = Names(kind=crd.kind(),
                  plural=crd.plural(),
                  singular=crd.singular(),
                  short_names=crd.short_names())

    return CRD(group=crd.group(), versions=[version], scope='Namespaced', names=names)
