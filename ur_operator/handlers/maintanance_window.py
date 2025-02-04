import kopf

from .handlers import config, uptime_robot
from .handler_util import *

ID_KEY = 'monitor_id'

def create(logger, props):
    resp = uptime_robot.new_m_window(**stringify_values(props))
    check_response(resp, logger, "MW", "create", jsonName="mwindow")

def update(logger, id, props):
    resp = uptime_robot.edit_m_window(id, **stringify_values(props))
    check_response(resp, logger, "MW", "update", id, "mwindow")

def delete(logger, id):
    check_response(uptime_robot.delete_m_window(id), logger, "MW", "delete", id)

def get_identifier(status: dict):
    return get_status_value(status, ID_KEY, on_update, on_create)

def on_create(name: str, spec: dict, logger, spec_to_request_dict: callable):
    return {ID_KEY: create(logger, spec_to_request_dict(name, spec))}

def on_update(name: str, spec: dict, status: dict, logger, diff: dict, spec_to_request_dict: callable):
    identifier = get_identifier(status)
    if identifier == -1:
        raise kopf.PermanentError(
            "was not able to determine the MW ID for update") from error

    update_payload = spec_to_request_dict(name, spec)

    if type_changed(diff):
        logger.info('maintenance window type changed, need to delete and recreate')
        delete(logger, identifier)
        identifier = create(logger, update_payload)
    else:
        update_payload.pop('type', None) # update does not accept type parameter
        identifier = update(logger, identifier, update_payload)

    return {ID_KEY: identifier}

def on_delete(status: dict, logger):
    identifier = get_identifier(status)
    if identifier == -1:
        raise kopf.PermanentError(
            "was not able to determine the MW ID for deletion") from error
    try:
        delete(logger, identifier)
    except Exception as error:
        raise kopf.PermanentError(f"deleting MW failed: {error}") from error

