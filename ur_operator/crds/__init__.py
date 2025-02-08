"""Contains CustomResourceDefinition classes and functions"""
from crds.alert_contact import AlertContactV1Beta1
from crds.maintenance_window import MaintenanceWindowV1Beta1
from crds.custom_resource_definition import CustomResourceDefinition
from crds.monitor import MonitorV1Beta1
from crds.ingress import IngressV1
from crds.psp import PspV1Beta1
from .common.crd_base import BaseCrd, GROUP, make_spec

__all__ = ['AlertContactV1Beta1', 'MaintenanceWindowV1Beta1',
           'CustomResourceDefinition', 'MonitorV1Beta1', 'PspV1Beta1',
           'BaseCrd', 'IngressV1', 'GROUP', 'make_spec']

ALL_CRDS: list[type[BaseCrd]] = [MonitorV1Beta1, PspV1Beta1,
                                 MaintenanceWindowV1Beta1, AlertContactV1Beta1]
