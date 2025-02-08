"""AlertContact CRD"""
import enum

from .common.crd_base import BaseCrd
from .common.property_types import v1string as string
from .common.util import camel_to_snake_case


@enum.unique
class AlertContactType(enum.Enum):  # pylint: disable=missing-class-docstring
    SMS = 1
    EMAIL = 2
    TWITTER_DM = 3
    BOXCAR = 4
    WEB_HOOK = 5
    PUSHBULLET = 6
    ZAPIER = 7
    PUSHOVER = 9
    HIPCHAT = 10
    SLACK = 11


class AlertContactV1Beta1(BaseCrd):
    """Class for AlertContactV1Beta1 CRD"""
    @staticmethod
    def plural():
        return 'alertcontacts'

    @staticmethod
    def singular():
        return 'alertcontact'

    @staticmethod
    def kind():
        return 'AlertContact'

    @staticmethod
    def short_names():
        return ['ac']

    @staticmethod
    def version():
        return 'v1beta1'

    @staticmethod
    def required_properties():
        return ['type', 'value']

# pylint: disable=line-too-long
    @staticmethod
    def properties():
        return {
            'type': string('the type of alert contact', AlertContactType),
            'value': string('the alert contact\'s mail address / phone number / URL / connection string'),
            'friendlyName': string('friendly name of the alert contact, defaults to name of the AlertContact object')
        }
# pylint: enable=line-too-long

    @staticmethod
    def spec_to_request_dict(name: str, spec: dict) -> dict:
        # convert all keys from camel to snake case
        request_dict = {camel_to_snake_case(k): v for k, v in spec.items()}
        request_dict['friendly_name'] = request_dict.get('friendly_name', name)

        # map enum values
        for key, enum_class in {
            'type': AlertContactType
        }.items():
            request_dict[key] = enum_class[request_dict[key]
                                           ].value if key in request_dict else None

        # drop None entries
        return {k: v for k, v in request_dict.items() if v is not None}
