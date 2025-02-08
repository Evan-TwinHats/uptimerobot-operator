"""UptimeRobot API client"""
import logging

import kopf
from uptimerobotpy import UptimeRobot as UR


class UptimeRobot:
    """UptimeRobot API client"""

    def __init__(self, config):
        try:
            ur_api_key = config.UPTIMEROBOT_API_KEY
        except KeyError as error:
            msg = f'Required environment variable {error.args[0]} has not been provided'
            logging.error(msg)
            raise RuntimeError(msg) from error

        self.api = UR(api_key=ur_api_key)
        resp = self.api.get_account_details()

        if resp['stat'] != 'ok':  # type: ignore
            logging.error('failed to authenticate against UptimeRobot API')
            raise RuntimeError(resp['error'])  # type: ignore

    @staticmethod
    def __check_response(resp, logger, thing, action, uid=None, json_name=None):
        json_name = json_name if json_name else thing.lower()
        if resp['stat'] == 'ok':
            if json_name in resp:
                uid = resp[json_name]['id']
            logger.info(
                f'{thing} with ID {uid} has been {action}d successfully')
            return uid
        if resp['error']['type'] == 'not_found':
            logger.info(
                f'Could not {action} {thing} with ID {uid} because does not exist.')
            return None

        id_desc = f" {uid}" if uid else ""
        raise kopf.PermanentError(
            f'failed to {action} {thing}{id_desc}: {resp["error"]}')

    @staticmethod
    def __stringify_values(props):
        return {k: str(v) for k, v in props.items()}
# pylint: disable=missing-function-docstring

    def create_psp(self, logger, props):
        resp = self.api.new_psp(type='1', **self.__stringify_values(props))
        return self.__check_response(resp, logger, "PSP", "create")

    def update_psp(self, logger, uid, props):
        resp = self.api.edit_psp(uid, **self.__stringify_values(props))
        return self.__check_response(resp, logger, "PSP", "update")

    def delete_psp(self, logger, uid):
        resp = self.api.delete_psp(uid)
        return self.__check_response(resp, logger, "PSP", "delete")

    def create_monitor(self, name: str, spec: dict, logger):
        resp = self.api.new_monitor(**spec)
        return self.__check_response(resp, logger, "monitor", "create", name)

    def update_monitor(self, spec: dict, uid, logger):
        resp = self.api.edit_monitor(uid, **spec)
        return self.__check_response(resp, logger, "monitor", "update", uid)

    def delete_monitor(self, logger, uid):
        resp = self.api.delete_monitor(uid)
        return self.__check_response(resp, logger, "monitor", "delete", uid)

    def create_mw(self, logger, props):
        resp = self.api.new_m_window(**self.__stringify_values(props))
        return self.__check_response(resp, logger, "MW", "create", json_name="mwindow")

    def update_mw(self, logger, uid, props):
        resp = self.api.edit_m_window(uid, **self.__stringify_values(props))
        return self.__check_response(resp, logger, "MW", "update", uid, "mwindow")

    def delete_mw(self, logger, uid):
        resp = self.api.delete_m_window(uid)
        return self.__check_response(resp, logger, "MW", "delete", uid)

    def create_ac(self, logger, props):
        resp = self.api.new_alert_contact(**self.__stringify_values(props))
        return self.__check_response(resp, logger, "alert contact", "delete", id, "alertcontact")

    def update_ac(self, logger, uid, props):
        resp = self.api.edit_alert_contact(
            uid, **self.__stringify_values(props))
        return self.__check_response(resp, logger, "alert contact", "update", uid, "alert_contact")

    def delete_ac(self, logger, uid):
        resp = self.api.delete_alert_contact(uid)
        return self.__check_response(resp, logger, "alert contact", "update", uid)
# pylint: enable=missing-function-docstring
