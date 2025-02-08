"""Handler class for MaintenanceWindows"""
import kopf

from api import UptimeRobot
from crds import MaintenanceWindowV1Beta1
from .common.handler_base import BaseHandler, type_changed


class MaintananceWindowHandler(BaseHandler):
    """Contains handler functions for MaintenanceWindows"""

    def __init__(self, ur: UptimeRobot, create_event_name, update_event_name):
        super().__init__(ur, MaintenanceWindowV1Beta1,
                         create_event_name, update_event_name, 'mw_id')
        self.build_request = MaintenanceWindowV1Beta1.spec_to_request_dict

    def on_create(self, name: str, spec: dict, logger):  # pylint: disable=missing-function-docstring
        return {self.id_key: self.uptime_robot.create_mw(logger, self.build_request(name, spec))}

    def on_update(self, name: str, spec: dict, status: dict, logger, diff: dict):  # pylint: disable=missing-function-docstring disable=too-many-arguments
        uid = self.get_identifier(status)
        update_payload = self.build_request(name, spec)

        if type_changed(diff):
            logger.info(
                'maintenance window type changed, need to delete and recreate')
            self.uptime_robot.delete_mw(logger, uid)
            uid = self.uptime_robot.create_mw(logger, update_payload)
        else:
            # update does not accept type parameter
            update_payload.pop('type', None)
            uid = self.uptime_robot.update_mw(logger, uid, update_payload)

        return {self.id_key: uid}

    def on_delete(self, status: dict, logger):  # pylint: disable=missing-function-docstring
        uid = self.get_identifier(status)
        if uid == -1:
            raise kopf.PermanentError(
                "was not able to determine the MW ID for deletion")
        try:
            self.uptime_robot.delete_mw(logger, uid)
        except Exception as error:
            raise kopf.PermanentError(
                f"deleting MW failed: {error}") from error
