"""Class for CustomResourceDefinition CRD. It's CRDs all the way down!"""
from .common.crd_base import BaseCrd


class CustomResourceDefinition(BaseCrd):
    """Class for CustomResourceDefinition CRD. It's CRDs all the way down!"""
    @staticmethod
    def group():
        return 'apiextensions.k8s.io'

    @staticmethod
    def plural():
        return ''

    @staticmethod
    def singular():
        return ''

    @staticmethod
    def kind():
        return 'CustomResourceDefinition'

    @staticmethod
    def short_names():
        return ['crd']

    @staticmethod
    def version():
        return 'v1'

    @staticmethod
    def required_properties():
        return []
