"""Handler class for AlertContacts"""
import kopf
from crds import AlertContactV1Beta1
from .common.handler_base import BaseHandler, type_changed, UptimeRobot


class AlertContactHandler(BaseHandler):
    """Contains handler functions for AlertContacts"""

    def __init__(self, ur: UptimeRobot, create_event_name, update_event_name):
        super().__init__(ur, AlertContactV1Beta1,
                         create_event_name, update_event_name, 'ac_id')

    def on_create(self, name: str, spec: dict, logger):  # pylint: disable=missing-function-docstring
        return {self.id_key: self.uptime_robot.create_ac(logger, self.build_request(name, spec))}

    def on_update(self, name: str, spec: dict, status: dict, logger, diff: dict):  # pylint: disable=missing-function-docstring
        identifier = self.get_identifier(status)
        if identifier == -1:
            raise kopf.PermanentError(
                "was not able to determine the AC ID for update")

        update_payload = AlertContactV1Beta1.spec_to_request_dict(name, spec)

        if type_changed(diff) or spec['type'] != 'WEB_HOOK':
            logger.info(
                'alert contact type changed or is not of type WEB_HOOK, need to delete and recreate')  # pylint: disable=line-too-long
            self.uptime_robot.delete_ac(logger, identifier)

            identifier = self.uptime_robot.create_ac(
                logger,
                update_payload
            )
        else:
            # update does not accept type parameter
            update_payload.pop('type', None)

            identifier = self.uptime_robot.update_ac(
                logger,
                identifier,
                update_payload
            )

        return {self.id_key: identifier}

    def on_delete(self, status: dict, logger):  # pylint: disable=missing-function-docstring
        identifier = self.get_identifier(status)
        if identifier == -1:
            raise kopf.PermanentError(
                "was not able to determine the AC ID for deletion")
        try:
            self.uptime_robot.delete_ac(logger, identifier)
        except Exception as error:
            raise kopf.PermanentError(
                f"deleting AC failed: {error}") from error
