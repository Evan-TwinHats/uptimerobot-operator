"""Class for IngressV1 CRD to be used by handlers"""
from .common.crd_base import BaseCrd


class IngressV1(BaseCrd):
    """Class for IngressV1 CRD to be used by handlers"""
    @staticmethod
    def group():
        return 'networking.k8s.io'

    @staticmethod
    def plural():
        return 'ingresses'

    @staticmethod
    def singular():
        return 'ingress'

    @staticmethod
    def kind():
        return 'Ingress'

    @staticmethod
    def short_names():
        return []

    @staticmethod
    def version():
        return 'v1'

    @staticmethod
    def required_properties():
        return []
