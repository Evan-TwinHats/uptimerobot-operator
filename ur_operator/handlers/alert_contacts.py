import kopf
from util import *
ID_KEY = 'ac_id'

def create(logger, props):
    resp = uptime_robot.new_alert_contact(**stringify_values(props))
    check_response(resp, logger, "alert contact", "delete", id, "alertcontact")

def update(logger, id, props):
    resp = uptime_robot.edit_alert_contact(id, **stringify_values(props))
    check_response(resp, logger, "alert contact", "update", id, "alert_contact")

def delete(logger, id):
    check_response(uptime_robot.delete_alert_contact(id), logger, "alert contact", "update", id)

def get_identifier(status: dict):
    return get_status_value(status, ID_KEY, on_ac_update, on_ac_create)

def on_create(name: str, spec: dict, logger, spec_to_request_dict: callable):
    return {ID_KEY: create(logger, spec_to_request_dict(name, spec))}

def on_update(name: str, spec: dict, status: dict, logger, diff: dict, spec_to_request_dict: callable):
    identifier = get_identifier(status)
    if identifier == -1:
        raise kopf.PermanentError(
            "was not able to determine the AC ID for update") from error

    update_payload = spec_to_request_dict(name, spec)

    if type_changed(diff) or spec['type'] != 'WEB_HOOK':
        logger.info('alert contact type changed or is not of type WEB_HOOK, need to delete and recreate')
        delete_ac(logger, identifier)

        identifier = create(
            logger,
            update_payload
        )
    else:
        update_payload.pop('type', None) # update does not accept type parameter

        identifier = update(
            logger,
            identifier,
            update_payload
        )

    return {ID_KEY: identifier}

def on_delete(status: dict, logger):
    identifier = get_identifier(status)
    if identifier == -1:
        raise kopf.PermanentError(
            "was not able to determine the AC ID for deletion") from error
    try: 
        delete(logger, identifier)
    except Exception as error:
        raise kopf.PermanentError(f"deleting AC failed: {error}") from error
