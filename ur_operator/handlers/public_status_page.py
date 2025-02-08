"""Handler class for PublicStatusPages"""
import kopf

from api import UptimeRobot
from crds import PspV1Beta1
from .common.handler_base import BaseHandler


class PSPHandler(BaseHandler):
    """Contains handler functions for PublicStatusPages"""

    def __init__(self, ur: UptimeRobot, create_event_name, update_event_name):
        super().__init__(ur, PspV1Beta1, create_event_name, update_event_name, 'psp_id')
        self.build_request_base = PspV1Beta1.spec_to_request_dict

    def __build_request_with_secrets(self, namespace, name, spec: dict):
        if 'password_secret' in spec:
            secret = self.k8s.get_secret(namespace, spec['password_secret'])

            spec['password'] = secret['password']
            spec.pop('password_secret')
        return self.build_request(name, spec)

    def on_create(self, namespace: str, name: str, spec: dict, logger):  # pylint: disable=missing-function-docstring
        spec = self.__build_request_with_secrets(namespace, name, spec)
        return {self.id_key: self.uptime_robot.create_psp(logger, spec)}

    def on_update(self, namespace: str, name: str, spec: dict, status: dict, logger):  # pylint: disable=missing-function-docstring disable=too-many-arguments
        uid = self.get_identifier(status)
        if uid == -1:
            raise kopf.PermanentError(
                "was not able to determine the PSP ID for update")

        spec = self.__build_request_with_secrets(namespace, name, spec)
        uid = self.uptime_robot.update_psp(logger, uid, spec)

        return {self.id_key: uid}

    def on_delete(self, status: dict, logger):  # pylint: disable=missing-function-docstring
        identifier = self.get_identifier(status)
        if identifier == -1:
            raise kopf.PermanentError(
                "was not able to determine the PSP ID for deletion")
        try:
            self.uptime_robot.delete_psp(logger, identifier)
        except Exception as error:
            raise kopf.PermanentError(
                f"deleting PSP failed: {error}") from error
