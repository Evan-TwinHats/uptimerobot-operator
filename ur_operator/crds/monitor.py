#!/usr/bin/env python3

import base64
import enum
import json

import kubernetes.client as k8s_client

from k8s import K8s
from .constants import GROUP, SINGULAR, PLURAL, KIND, SHORT_NAMES, VERSION
from .utils import camel_to_snake_case


class MonitorType(enum.Enum):
    HTTP = 1
    HTTPS = 1
    KEYWORD = 2
    PING = 3
    PORT = 4
    HEARTBEAT = 5


@enum.unique
class MonitorSubType(enum.Enum):
    HTTP = 1
    HTTPS = 2
    FTP = 3
    SMTP = 4
    POP3 = 5
    IMAP = 6
    CUSTOM = 99


@enum.unique
class MonitorHttpMethod(enum.Enum):
    HEAD = 1
    GET = 2
    POST = 3
    PUT = 4
    PATCH = 5
    DELETE = 6
    OPTIONS = 7


@enum.unique
class MonitorKeywordType(enum.Enum):
    EXISTS = 1
    NOT_EXISTS = 2


@enum.unique
class MonitorStatus(enum.Enum):
    PAUSED = 0
    NOT_CHECKED_YET = 1


@enum.unique
class MonitorHttpAuthType(enum.Enum):
    BASIC_AUTH = 1
    DIGEST = 2


@enum.unique
class MonitorPostType(enum.Enum):
    KEY_VALUE = 1
    RAW = 2


@enum.unique
class MonitorPostContentType(enum.Enum):
    TEXT_HTML = 0
    APPLICATION_JSON = 1


class MonitorV1Beta1:
    required_props = ['url', 'type']

    spec_properties = {
        'url': k8s_client.V1JSONSchemaProps(
            type='string',
            description='URL that will be monitored'
        ),
        'path': k8s_client.V1JSONSchemaProps(
            type='string',
            description='Path that will be appended to the URL to be monitored'
        ),
        'type': k8s_client.V1JSONSchemaProps(
            type='string',
            enum=list(
                MonitorType.__members__.keys()),
            description=f'Type of monitor, one of: {",".join(list(MonitorType.__members__.keys()))}'
        ),
        'friendlyName': k8s_client.V1JSONSchemaProps(
            type='string',
            description='Friendly name of monitor, defaults to name of UptimeRobotMonitor object'
        ),
        'subType': k8s_client.V1JSONSchemaProps(
            type='string',
            enum=list(
                MonitorSubType.__members__.keys()),
            description=f'Subtype of monitor, one of: {",".join(list(MonitorType.__members__.keys()))}'
        ),
        'port': k8s_client.V1JSONSchemaProps(
            type='integer',
            description=f'Port to monitor when using monitor sub type {MonitorType.PORT.name}'
        ),
        'keywordType': k8s_client.V1JSONSchemaProps(
            type='string',
            enum=list(
                MonitorKeywordType.__members__.keys()),
            description=f'Keyword type when using monitor type {MonitorType.KEYWORD.name}, one of: {",".join(list(MonitorKeywordType.__members__.keys()))}'
        ),
        'keywordValue': k8s_client.V1JSONSchemaProps(
            type='string',
            description=f'Keyword value when using monitor type {MonitorType.KEYWORD.name}'
        ),
        'interval': k8s_client.V1JSONSchemaProps(
            type='integer',
            multiple_of=60.,
            description='The interval for the monitoring check (300 seconds by default)'
        ),
        'httpUsername': k8s_client.V1JSONSchemaProps(
            type='string',
            description=f'Used for password protected pages when using monitor type {MonitorType.HTTP.name},{MonitorType.HTTPS.name} or {MonitorType.KEYWORD.name}, deprecated: use httpAuthSecret'
        ),
        'httpPassword': k8s_client.V1JSONSchemaProps(
            type='string',
            description=f'Used for password protected pages when using monitor type {MonitorType.HTTP.name},{MonitorType.HTTPS.name} or {MonitorType.KEYWORD.name}, deprecated: use httpAuthSecret'
        ),
        'httpAuthSecret': k8s_client.V1JSONSchemaProps(
            type='string',
            description=f'reference to a Kubernetes secret in the same namespace containing user and password for password protected pages when using monitor type {MonitorType.HTTP.name},{MonitorType.HTTPS.name} or {MonitorType.KEYWORD.name}'
        ),
        'httpAuthType': k8s_client.V1JSONSchemaProps(
            type='string',
            enum=list(
                MonitorHttpAuthType.__members__.keys()),
            description=f'Used for password protected pages when using monitor type {MonitorType.HTTP.name},{MonitorType.HTTPS.name} or {MonitorType.KEYWORD.name}, one of: {",".join(list(MonitorHttpAuthType.__members__.keys()))}'
        ),
        'httpMethod': k8s_client.V1JSONSchemaProps(
            type='string',
            enum=list(
                MonitorHttpMethod.__members__.keys()),
            description=f'The HTTP method to be used, one of: {",".join(list(MonitorHttpMethod.__members__.keys()))}'
        ),
        'postType': k8s_client.V1JSONSchemaProps(
            type='string',
            enum=list(
                MonitorPostType.__members__.keys()),
            description='The format of data to be sent with POST, PUT, PATCH, DELETE, OPTIONS requests'
        ),
        'postContentType': k8s_client.V1JSONSchemaProps(
            type='string',
            enum=list(
                MonitorPostContentType.__members__.keys()),
            description=f'The Content-Type header to be sent with POST, PUT, PATCH, DELETE, OPTIONS requests, one of: {",".join(list(MonitorPostContentType.__members__.keys()))}'
        ),
        'postValue': k8s_client.V1JSONSchemaProps(
            type='object',
            description='The data to be sent with POST, PUT, PATCH, DELETE, OPTIONS requests',
            x_kubernetes_preserve_unknown_fields=True
        ),
        'customHttpHeaders': k8s_client.V1JSONSchemaProps(
            type='object',
            description='Custom HTTP headers to be sent along monitor request, formatted as JSON',
            x_kubernetes_preserve_unknown_fields=True
        ),
        'customHttpStatuses': k8s_client.V1JSONSchemaProps(
            type='string',
            description='Allows to define HTTP status codes that will be handled as up or down, e.g. 404:0_200:1 to accept 404 as down and 200 as up'
        ),
        'ignoreSslErrors': k8s_client.V1JSONSchemaProps(
            type='boolean',
            description='Flag to ignore SSL certificate related issues'
        ),
        'alertContacts': k8s_client.V1JSONSchemaProps(
            type='string',
            description='Alert contacts to be notified when monitor goes up or down. For syntax check https://uptimerobot.com/api/#newMonitorWrap'
        ),
        'mwindows': k8s_client.V1JSONSchemaProps(
            type='string',
            description='Maintenance window IDs for this monitor'
        )
    }

    crd = k8s_client.V1CustomResourceDefinition(
        api_version='apiextensions.k8s.io/v1',
        kind='CustomResourceDefinition',
        metadata=k8s_client.V1ObjectMeta(name=f'{PLURAL}.{GROUP}'),
        spec=k8s_client.V1CustomResourceDefinitionSpec(
            group=GROUP,
            versions=[k8s_client.V1CustomResourceDefinitionVersion(
                name=VERSION,
                served=True,
                storage=True,
                schema=k8s_client.V1CustomResourceValidation(
                    open_apiv3_schema=k8s_client.V1JSONSchemaProps(
                        type='object',
                        properties={
                            'spec': k8s_client.V1JSONSchemaProps(
                                type='object',
                                required=required_props,
                                properties=spec_properties
                            ),
                            'status': k8s_client.V1JSONSchemaProps(
                                type='object',
                                x_kubernetes_preserve_unknown_fields=True
                            )
                        }
                    )
                ),
                additional_printer_columns=[
                    k8s_client.V1CustomResourceColumnDefinition(
                        description = 'Friendly Name',
                        json_path = '.spec.friendlyName',
                        name = 'Friendly Name',
                        type = 'string'
                    ),
                    k8s_client.V1CustomResourceColumnDefinition(
                        description = 'Ingress',
                        json_path = '.metadata.ownerReferences[0].name',
                        name = 'Ingress',
                        type = 'string'
                    ),
                    k8s_client.V1CustomResourceColumnDefinition(
                        description = 'Monitor Type',
                        json_path = '.spec.type',
                        name = 'Type',
                        type = 'string'
                    ),
                    k8s_client.V1CustomResourceColumnDefinition(
                        description = 'Monitored URL',
                        json_path = '.spec.url',
                        name = 'URL',
                        type = 'string'
                    ),
                    k8s_client.V1CustomResourceColumnDefinition(
                        description = 'Monitored Path',
                        json_path = '.spec.path',
                        name = 'Path',
                        type = 'string'
                    )
                ]
            )],
            scope='Namespaced',
            names=k8s_client.V1CustomResourceDefinitionNames(
                plural=PLURAL,
                singular=SINGULAR,
                kind=KIND,
                short_names=SHORT_NAMES
            )
        )
    )

    @staticmethod
    def spec_to_request_dict(namespace:str, name: str, spec: dict) -> dict:
        k8s = K8s()

        # convert all keys from camel to snake case
        request_dict = {camel_to_snake_case(k): v for k, v in spec.items()}
        request_dict['friendly_name'] = request_dict.get('friendly_name', name)
        request_dict['type'] = MonitorType[spec['type']].value

        if 'path' in request_dict and spec['type'] in ['HTTP','HTTPS','KEYWORD']:
            request_dict['url'] = request_dict['url'] + request_dict.pop('path')
            
        if 'http_auth_secret' in request_dict:
            secret = k8s.get_secret(namespace, request_dict['http_auth_secret'])

            request_dict['http_username'] = base64.b64decode(secret.data['username']).decode()
            request_dict['http_password'] = base64.b64decode(secret.data['password']).decode()
            request_dict.pop('http_auth_secret')

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
    def annotations_to_spec_dict(annotations: dict) -> dict:
        spec = {}

        for key, value in annotations.items():
            if key not in MonitorV1Beta1.spec_properties:
                continue
            
            if MonitorV1Beta1.spec_properties[key].type == 'integer':
                spec[key] = int(value)
            elif MonitorV1Beta1.spec_properties[key].type == 'object':
                spec[key] = json.loads(value)
            else:
                spec[key] = value
        return spec

    @staticmethod
    def construct_k8s_ur_monitor_body(namespace, ingressName=None, **spec):
        metadata = {
            'namespace': namespace
        }
        if spec['type'] == 'KEYWORD' and 'keywordType' not in spec:
            spec['keywordType'] = 'NOT_EXISTS'
        
        if ingressName:
            metadata['name'] = ingressName
        return {
            'apiVersion': f'{GROUP}/{VERSION}',
            'kind': KIND,
            'metadata': metadata,
            'spec': spec
        }


