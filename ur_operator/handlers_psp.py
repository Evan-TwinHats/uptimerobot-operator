import kopf

from crds.psp import PspV1Beta1
from crds.constants import GROUP
from .handlers import config, uptime_robot
from .handler_util import *
ID_KEY = 'psp_id'

def create(logger, props):
    resp = uptime_robot.new_psp(type='1', **stringify_values(props))
    check_response(resp, logger, "PSP", "create")
    
def update(logger, id, props):
    resp = uptime_robot.edit_psp(id, **stringify_values(props))
    check_response(resp, logger, "PSP", "update")

def delete(logger, id):
    check_response(uptime_robot.delete_psp(id), logger, "PSP", "delete")

def get_identifier(status: dict):
    return get_status_value(status, ID_KEY, on_update, on_create)

@kopf.on.create(GROUP, VERSION, PspV1Beta1.plural)
def on_create(namespace: str, name: str, spec: dict, logger, **_):
    return {ID_KEY: create(logger, PspV1Beta1.spec_to_request_dict(namespace, name, spec))}

@kopf.on.update(GROUP, VERSION, PspV1Beta1.plural)
def on_update(namespace: str, name: str, spec: dict, status: dict, logger, **_):
    identifier = get_identifier(status)
    if identifier == -1:
        raise kopf.PermanentError(
            "was not able to determine the PSP ID for update") from error

    identifier = update(logger, identifier, PspV1Beta1.spec_to_request_dict(namespace, name, spec))

    return {ID_KEY: identifier}

@kopf.on.delete(GROUP, VERSION, PspV1Beta1.plural)
def on_delete(status: dict, logger, **_):
    identifier = get_identifier(status)
    if identifier == -1:
        raise kopf.PermanentError(
            "was not able to determine the PSP ID for deletion") from error
    try:
        delete(logger, identifier)
    except Exception as error:
        raise kopf.PermanentError(f"deleting PSP failed: {error}") from error
