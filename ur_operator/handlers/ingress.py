"""Handler class for Ingresses"""
import hashlib

from api import UptimeRobot
from crds.monitor import MonitorV1Beta1
from .common.handler_base import BaseHandler, format_url


class IngressHandler(BaseHandler):
    """Contains handler functions for Ingresses"""

    def __init__(self, ur: UptimeRobot, create_event_name, update_event_name):
        super().__init__(ur, MonitorV1Beta1, create_event_name, update_event_name, 'monitor_id')

    def on_create(self, name: str, namespace: str, annotations: dict, spec: dict, logger):  # pylint: disable=missing-function-docstring
        logger.info(f"Creating monitors for new ingress {name}")
        self.__create_or_update_crds(
            name, namespace, annotations, spec, logger)

    def on_update(self, name: str, namespace: str, annotations: dict, spec: dict, logger):  # pylint: disable=missing-function-docstring
        logger.info(f"Updating monitors for ingress {name}")
        self.__create_or_update_crds(
            name, namespace, annotations, spec, logger)

    def __create_or_update_crds(self, ingress_name: str, namespace: str,
                                annotations: dict, spec: dict, logger):  # pylint: disable=too-many-arguments
        def match_crd_to_rule(rule: dict, crd: dict):
            return generate_monitor_name(rule) == crd['metadata']['name']

        def match_crd_to_ingress(crd: dict):
            return ('ownerReferences' in crd['metadata']
                    and crd['metadata']['ownerReferences'][0]['name'] == ingress_name)

        def generate_monitor_name(rule: dict):
            host = rule['host']
            port = rule['port'] if 'port' in rule else ''
            path = rule['path'] if 'path' in rule else ''

            sha = hashlib.sha256()
            sha.update(f"{ingress_name}{host}{path}{port}".encode())
            digest = sha.hexdigest()[:8]
            return f"{host}-{digest}"

        if self.config.DISABLE_INGRESS_HANDLING:
            logger.debug('handling of Ingress resources has been disabled')
            return

        monitor_prefix = f'{self.crd.group()}/monitor.'
        monitor_spec = {k.replace(monitor_prefix, ''): v
                        for k, v in annotations.items() if k.startswith(monitor_prefix)}

        if 'type' not in monitor_spec:
            logger.info(
                f"Type not specified. Defaulting to {self.config.DEFAULT_MONITOR_TYPE}")
            monitor_spec['type'] = self.config.DEFAULT_MONITOR_TYPE

        rules = []
        for rule in spec['rules']:
            if 'host' not in rule:
                continue

            host = rule['host']

            # Filter out wildcard, unqualified, and excluded domains
            if (host.startswith('*')
                or '.' not in host
                    or host.endswith(self.config.EXCLUDED_DOMAINS)):
                if host is not None:
                    logger.info(
                        f'Excluding rule for {host} as wildcard, unqualified, or excluded.')
            else:
                rules.append(rule)
        crds = self.k8s.list_resource(namespace) 
        for crd in crds:
            if (match_crd_to_ingress(crd)
                    and not any(match_crd_to_rule(rule, crd) for rule in rules)):
                self.k8s.delete_resource(namespace, crd['metadata']['name'])
                logger.info('deleted obsolete UptimeRobotMonitor object')

        for rule in rules:
            host = rule['host']

            format_url(monitor_spec, host)

            name = generate_monitor_name(rule)
            body = MonitorV1Beta1.validate_spec(monitor_spec)

            if any(match_crd_to_rule(rule, crd) for crd in crds):
                self.k8s.update_resource(namespace, name, body, True)
                logger.info(f'Updated monitor for URL {host}: {body}')
            else:
                self.k8s.create_resource(namespace, name, body, True)
                logger.info(f'Created monitor for URL {host}: {body}')
