"""The UptimeRobotMonitor CustomResourceDefinition and related Enums & functions"""

import enum
import json

from .common.crd_base import BaseCrd
from .common.property_types import v1string, v1object, v1boolean, v1integer

from .common.util import camel_to_snake_case, printer_column


class MonitorType(enum.Enum):  # pylint: disable=missing-class-docstring
    HTTP = 1
    HTTPS = 1
    KEYWORD = 2
    PING = 3
    PORT = 4
    HEARTBEAT = 5


@enum.unique
class MonitorSubType(enum.Enum):  # pylint: disable=missing-class-docstring
    HTTP = 1
    HTTPS = 2
    FTP = 3
    SMTP = 4
    POP3 = 5
    IMAP = 6
    CUSTOM = 99


@enum.unique
class MonitorHttpMethod(enum.Enum):  # pylint: disable=missing-class-docstring
    HEAD = 1
    GET = 2
    POST = 3
    PUT = 4
    PATCH = 5
    DELETE = 6
    OPTIONS = 7


@enum.unique
class MonitorKeywordType(enum.Enum):  # pylint: disable=missing-class-docstring
    EXISTS = 1
    NOT_EXISTS = 2


@enum.unique
class MonitorStatus(enum.Enum):  # pylint: disable=missing-class-docstring
    PAUSED = 0
    NOT_CHECKED_YET = 1


@enum.unique
class MonitorHttpAuthType(enum.Enum):  # pylint: disable=missing-class-docstring
    BASIC_AUTH = 1
    DIGEST = 2


@enum.unique
class MonitorPostType(enum.Enum):  # pylint: disable=missing-class-docstring
    KEY_VALUE = 1
    RAW = 2


@enum.unique
class MonitorPostContentType(enum.Enum):  # pylint: disable=missing-class-docstring
    TEXT_HTML = 0
    APPLICATION_JSON = 1


class MonitorV1Beta1(BaseCrd):
    """The UptimeRobotMonitor CustomResourceDefinition"""

    @staticmethod
    def plural():
        return 'uptimerobotmonitors'

    @staticmethod
    def singular():
        return 'uptimerobotmonitor'

    @staticmethod
    def kind():
        return 'UptimeRobotMonitor'

    @staticmethod
    def short_names():
        return ['urm']

    @staticmethod
    def version():
        return 'v1beta1'

    @staticmethod
    def required_properties():
        return ['url']

# pylint: disable=line-too-long
    @staticmethod
    def properties():
        return {
            'url': v1string('URL that will be monitored'),
            'path': v1string('Path that will be appended to the URL to be monitored'),
            'type': v1string('Type of monitor', MonitorType),
            'friendlyName': v1string('Friendly name of monitor, defaults to name of UptimeRobotMonitor object'),
            'subType': v1string('SubType of monitor', MonitorSubType),
            'port': v1integer(f'Port to monitor when using monitor sub type {MonitorType.PORT.name}'),
            'keywordType': v1string(f'Keyword type when using monitor type {MonitorType.KEYWORD.name}', MonitorKeywordType),
            'keywordValue': v1string(f'Keyword value when using monitor type {MonitorType.KEYWORD.name}'),
            'interval': v1integer('The interval for the monitoring check (300 seconds by default)', 60.),
            'httpAuthSecret': v1string(f'reference to a Kubernetes secret in the same namespace containing user and password for password protected pages when using monitor type {MonitorType.HTTP.name},{MonitorType.HTTPS.name} or {MonitorType.KEYWORD.name}'),
            'httpAuthType': v1string(f'Used for password protected pages when using monitor type {MonitorType.HTTP.name},{MonitorType.HTTPS.name} or {MonitorType.KEYWORD.name}', MonitorHttpAuthType),
            'httpMethod': v1string('The HTTP method to be used', MonitorHttpMethod),
            'postType': v1string('The format of data to be sent with POST, PUT, PATCH, DELETE, OPTIONS requests', MonitorPostType),
            'postContentType': v1string('The Content-Type header to be sent with POST, PUT, PATCH, DELETE, OPTIONS requests', MonitorPostContentType),
            'postValue': v1object('The data to be sent with POST, PUT, PATCH, DELETE, OPTIONS requests'),
            'customHttpHeaders': v1object('Custom HTTP headers to be sent along monitor request, formatted as JSON'),
            'customHttpStatuses': v1string('Allows to define HTTP status codes that will be handled as up or down, e.g. 404:0_200:1 to accept 404 as down and 200 as up'),
            'ignoreSslErrors': v1boolean('Flag to ignore SSL certificate related issues'),
            'alertContacts': v1string('Alert contacts to be notified when monitor goes up or down. For syntax check https://uptimerobot.com/api/#newMonitorWrap'),
            'mwindows': v1string('Maintenance window IDs for this monitor')
        }
# pylint: enable=line-too-long

    @staticmethod
    def printer_columns():
        return [
            printer_column('Friendly Name', '.spec.friendlyName'),
            printer_column('Ingress', '.metadata.ownerReferences[0].name'),
            printer_column('Monitor Type', '.spec.type'),
            printer_column('Monitored URL', '.spec.url'),
            printer_column('Monitored Path', '.spec.path')
        ]

    @staticmethod
    def spec_to_request_dict(name: str, spec: dict) -> dict:
        # convert all keys from camel to snake case
        request_dict = {camel_to_snake_case(k): v for k, v in spec.items()}
        request_dict['friendly_name'] = request_dict.get('friendly_name', name)
        request_dict['type'] = MonitorType[spec['type']].value

        if 'path' in request_dict and spec['type'] in ['HTTP', 'HTTPS', 'KEYWORD']:
            request_dict['url'] = request_dict['url'] + \
                request_dict.pop('path')

        # map enum values
        for key, enum_class in {
            'sub_type': MonitorSubType,
            'keyword_type': MonitorKeywordType,
            'http_auth_type': MonitorHttpAuthType,
            'http_method': MonitorHttpMethod,
            'post_type': MonitorPostType,
            'post_content_type': MonitorPostContentType
        }.items():
            request_dict[key] = enum_class[request_dict[key]
                                           ].value if key in request_dict else None
        # drop None entries

        return {k: v for k, v in request_dict.items() if v is not None}

    @staticmethod
    def validate_spec(proto_spec: dict) -> dict:
        """Parse each string value in a dict into the correct type based on its key. 
        Also sets the keywordType to NOT_EXISTS if it hasn't been otherwise specified"""
        spec = {}

        for key, value in proto_spec.items():
            if key not in MonitorV1Beta1.properties():
                continue

            if MonitorV1Beta1.properties()[key].type == 'integer':
                spec[key] = int(value)
            elif MonitorV1Beta1.properties()[key].type == 'object' and isinstance(value, str):
                spec[key] = json.loads(value)
            else:
                spec[key] = value

        if spec['type'] == 'KEYWORD' and 'keywordType' not in spec:
            spec['keywordType'] = 'NOT_EXISTS'

        return spec
