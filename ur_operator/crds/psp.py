"""Class for PspV1Beta1 CRD"""
import enum

from .common.crd_base import BaseCrd
from .common.property_types import v1string as string, v1boolean as boolean
from .common.util import camel_to_snake_case


@enum.unique
class PspStatus(enum.Enum):  # pylint: disable=missing-class-docstring
    PAUSED = 0
    ACTIVE = 1


@enum.unique
class PspSort(enum.Enum):  # pylint: disable=missing-class-docstring
    FRIENDLY_NAME_A_Z = 1
    FRIENDLY_NAME_Z_A = 2
    STATUS_UP_DOWN_PAUSED = 3
    STATUS_DOWN_UP_PAUSED = 4


class PspV1Beta1(BaseCrd):
    """Class for PspV1Beta1 CRD"""

    @staticmethod
    def plural():
        return 'publicstatuspages'

    @staticmethod
    def singular():
        return 'publicstatuspage'

    @staticmethod
    def kind():
        return 'PublicStatusPage'

    @staticmethod
    def short_names():
        return ['psp']

    @staticmethod
    def version():
        return 'v1beta1'

    @staticmethod
    def required_properties():
        return ['monitors']
# pylint: disable=line-too-long

    @staticmethod
    def properties():
        return {
            'monitors': string('the list of monitor IDs to be displayed in status page (the values are seperated with "-" or 0 for all monitors)'),
            'friendlyName': string('Friendly name of public status page, defaults to name of PublicStatusPage object'),
            'customDomain': string('the domain or subdomain that the status page will run on'),
            'password': string('the password for the status page, deprecated: use passwordSecret'),
            'passwordSecret': string('reference to a Kubernetes secret in the same namespace containing the password for the status page'),
            'sort': string('the sorting of the monitors on the status page', PspSort),
            'status': string('the status of the status page', PspStatus),
            'hideUrlLinks': boolean('Flag to remove the UptimeRobot link from the status page (pro plan feature)')
        }
# pylint: enable=line-too-long

    @staticmethod
    def spec_to_request_dict(name: str, spec: dict) -> dict:

        # convert all keys from camel to snake case
        request_dict = {camel_to_snake_case(k): v for k, v in spec.items()}
        request_dict['friendly_name'] = request_dict.get('friendly_name', name)

        # map enum values
        for key, enum_class in {
            'sort': PspSort,
            'status': PspStatus
        }.items():
            request_dict[key] = enum_class[request_dict[key]
                                           ].value if key in request_dict else None

        # drop None entries
        return {k: v for k, v in request_dict.items() if v is not None}
