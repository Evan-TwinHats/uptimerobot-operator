import kopf
import hashlib

from crds.monitor import MonitorV1Beta1, MonitorType
from crds.constants import GROUP
from .handlers import config, uptime_robot
from .handler_util import *

ID_KEY = 'monitor_id'

def create(namespace: str, name: str, spec: dict, logger):  
    request_dict = MonitorV1Beta1.spec_to_request_dict(namespace, name, spec)
    check_response(uptime_robot.new_monitor(**request_dict), logger, "monitor", "create", name)   

def update(namespace: str, name: str, spec: dict, logger, id): 
    request_dict = MonitorV1Beta1.spec_to_request_dict(namespace, name, spec)
    check_response(uptime_robot.edit_monitor(id, **request_dict), logger, "monitor", "update", id)

def delete(logger, id):
    check_response(uptime_robot.delete_monitor(id), logger, "monitor", "delete", id)

def set_defaults(namespace: str, monitor_name: str, monitor_body: dict, logger):
    updated_body = {k:v for k,v in monitor_body.items()}
   
    formatUrl(updated_body, updated_body['url'])

    if 'customHttpHeaders' not in updated_body and config.DEFAULT_HEADERS != {}:
        logger.info('CustomHttpHeaders not set on monitor. Using user-define defaults.')
        updated_body['customHttpHeaders'] = config.DEFAULT_HEADERS

    k8s.update_k8s_crd_obj_with_body(MonitorV1Beta1, namespace, monitor_name, 
        MonitorV1Beta1.construct_k8s_ur_monitor_body(namespace, monitor_name, **updated_body))
    return updated_body

def get_identifier(status: dict):
    return get_status_value(status, ID_KEY, on_update, on_create)

@kopf.on.create(GROUP, MonitorV1Beta1.version, MonitorV1Beta1.plural)
def on_create(namespace: str, name: str, spec: dict, logger, **_):
    logger.info(f"Monitor created: {name}")
    spec = set_defaults(namespace, name, spec, logger)
    return {ID_KEY: create_monitor(namespace, name, spec, logger)}

@kopf.on.update(GROUP, MonitorV1Beta1.version, MonitorV1Beta1.plural)
def on_update(namespace: str, name: str, spec: dict, status: dict, diff: list, logger, **_):
    logger.info(f"Monitor updated: {name}")
    spec = set_defaults(namespace, name, spec, logger)
    identifier = get_identifier(status)
    if identifier == -1:
        raise kopf.PermanentError(
            "was not able to determine the monitor ID for update") from error
    if type_changed(diff):
        logger.info('monitor type changed, need to delete and recreate')
        delete_monitor(logger, identifier)
        return {ID_KEY: create_monitor(namespace, name, spec, logger)}
    else:
        return {ID_KEY: update_monitor(namespace, name, spec, logger, identifier)}
    
@kopf.on.delete(GROUP, MonitorV1Beta1.version, MonitorV1Beta1.plural)
def on_delete(status: dict, logger, **_):
    identifier = get_identifier(status)
    if identifier == -1:
        raise kopf.PermanentError(
            "was not able to determine the monitor ID for deletion") from error
    try:
        delete_monitor(logger, identifier)
    except Exception as error:
        raise kopf.PermanentError(f"deleting monitor failed: {error}") from error
