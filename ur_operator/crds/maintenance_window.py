"""Class for MaintenanceWindow CRD"""
import enum

from .common.crd_base import BaseCrd
from .common.property_types import v1string as string, v1number as number
from .common.util import camel_to_snake_case


@enum.unique
class MaintenanceWindowType(enum.Enum):  # pylint: disable=missing-class-docstring
    ONCE = 1
    DAILY = 2
    WEEKLY = 3
    MONTHLY = 4


class MaintenanceWindowV1Beta1(BaseCrd):
    """Class for MaintenanceWindowV1Beta1 CRD"""
    @staticmethod
    def plural():
        return 'maintenancewindows'

    @staticmethod
    def singular():
        return 'maintenancewindow'

    @staticmethod
    def kind():
        return 'MaintenanceWindow'

    @staticmethod
    def short_names():
        return ['mw']

    @staticmethod
    def version():
        return 'v1beta1'

    @staticmethod
    def required_properties():
        return ['type', 'startTime', 'duration']

# pylint: disable=line-too-long
    @staticmethod
    def properties():
        return {
            'type': string('the type of maintenance window', MaintenanceWindowType),
            'startTime': string(f'the start time of the maintenance window, in seconds since epoch for type {MaintenanceWindowType.ONCE}, in HH:mm format for the other types'),
            'duration': number('the number of seconds the maintenance window will be active'),
            'friendlyName': string('friendly name of the maintenance window, defaults to name of the MaintenanceWindow object'),
            'value': string(f'allows to specify the maintenance window selection, e.g. 2-4-5 for Tuesday-Thursday-Friday or 10-17-26 for the days of the month, only valid and required for {MaintenanceWindowType.WEEKLY} and {MaintenanceWindowType.MONTHLY}')
        }
# pylint: enable=line-too-long

    @staticmethod
    def spec_to_request_dict(name: str, spec: dict) -> dict:
        # convert all keys from camel to snake case
        request_dict = {camel_to_snake_case(k): v for k, v in spec.items()}
        request_dict['friendly_name'] = request_dict.get('friendly_name', name)
        request_dict['value'] = request_dict.get('value', '')

        # map enum values
        for key, enum_class in {
            'type': MaintenanceWindowType
        }.items():
            request_dict[key] = enum_class[request_dict[key]
                                           ].value if key in request_dict else None

        # drop None entries

        return {k: v for k, v in request_dict.items() if v is not None}
