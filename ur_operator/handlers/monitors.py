"""Handler class for UptimeRobotMonitors"""
import kopf
from api import UptimeRobot
from crds import MonitorV1Beta1
from .common.handler_base import BaseHandler, format_url, type_changed


class MonitorHandler(BaseHandler):
    """Contains handler functions for UptimeRobotMonitors"""

    def __init__(self, ur: UptimeRobot, create_event_name, update_event_name):
        super().__init__(ur, MonitorV1Beta1, create_event_name, update_event_name, 'monitor_id')

    def __build_request_with_secrets(self, namespace: str, name: str, request_dict: dict):
        if 'http_auth_secret' in request_dict:
            secret = self.k8s.get_secret(
                namespace, request_dict['http_auth_secret'])

            request_dict['http_username'] = secret['username']
            request_dict['http_password'] = secret['password']
            request_dict.pop('http_auth_secret')

        if 'http_auth_headers_secret' in request_dict:
            secret = self.k8s.get_secret(
                namespace, request_dict['http_auth_headers_secret'])

            client_id = secret['CLIENT_ID']
            client_id_header = secret['CLIENT_ID_HEADER']
            client_secret = secret['CLIENT_SECRET']
            client_secret_header = secret['CLIENT_SECRET_HEADER']

            request_dict['http_password'] = secret['password']
            request_dict['customHttpHeaders'][client_id_header] = client_id
            request_dict['customHttpHeaders'][client_secret_header] = client_secret
            request_dict.pop('http_auth_secret')
        return self.build_request(name, request_dict)

    def __set_defaults(self, namespace: str, monitor_name: str, monitor_body: dict, logger):
        updated_body = dict(monitor_body.items())
        logger.info(f"Setting defaults for monitor {monitor_body}")
        format_url(updated_body, updated_body['url'])
        if 'type' not in updated_body:
            logger.info(
                f"Type not specified. Defaulting to {self.config.DEFAULT_MONITOR_TYPE}")
            updated_body['type'] = self.config.DEFAULT_MONITOR_TYPE
        if 'customHttpHeaders' not in updated_body and self.config.DEFAULT_HEADERS:
            logger.info(
                'CustomHttpHeaders not set on monitor. Using user-defined defaults.')
            updated_body['customHttpHeaders'] = self.config.DEFAULT_HEADERS
        k8s_body = MonitorV1Beta1.validate_spec(updated_body)
        logger.debug(f'Validated Monitor spec for set_defaults: {k8s_body}')
        self.k8s.update_resource(namespace, monitor_name, k8s_body, logger)
        return updated_body

    def on_create(self, namespace: str, name: str, spec: dict, logger):  # pylint: disable=missing-function-docstring
        logger.info(f"Monitor created: {name}: {spec}")
        spec = self.__set_defaults(namespace, name, spec, logger)
        spec = self.__build_request_with_secrets(namespace, name, spec)
        return {self.id_key: self.uptime_robot.create_monitor(name, spec, logger)}

    def on_update(self, namespace: str, name: str, spec: dict, status: dict, diff, logger):  # pylint: disable=missing-function-docstring
        logger.info(f"Monitor updated: {name}")
        spec = self.__set_defaults(namespace, name, spec, logger)
        spec = self.__build_request_with_secrets(namespace, name, spec)
        uid = self.get_identifier(status)
        if type_changed(diff):
            logger.info('monitor type changed, need to delete and recreate')
            self.uptime_robot.delete_monitor(logger, uid)
            return {self.id_key: self.uptime_robot.create_monitor(name, spec, logger)}
        return {self.id_key: self.uptime_robot.update_monitor(spec, uid, logger)}

    def on_delete(self, status: dict, logger):  # pylint: disable=missing-function-docstring
        try:
            identifier = self.get_identifier(status)
            self.uptime_robot.delete_monitor(logger, identifier)
        except Exception as error:
            raise kopf.PermanentError(
                f"deleting monitor failed: {error}") from error
