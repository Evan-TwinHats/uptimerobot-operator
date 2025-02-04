import logging
import hashlib

import kubernetes.config as k8s_config
import kubernetes.client as k8s_client
import kopf

from crds.monitor import MonitorV1Beta1, MonitorType
from crds.psp import PspV1Beta1
from crds.maintenance_window import MaintenanceWindowV1Beta1
from crds.alert_contact import AlertContactV1Beta1, AlertContactType
from crds.constants import GROUP, VERSION, SINGULAR, PLURAL
from k8s import K8s
import uptimerobot 
from config import Config
import json

MONITOR_ID_KEY = 'monitor_id'
PSP_ID_KEY = 'psp_id'
MW_ID_KEY = 'mw_id'
AC_ID_KEY = 'ac_id'

config = Config()
uptime_robot = None
k8s = None


# disable liveness check request logs
logging.getLogger('aiohttp.access').setLevel(logging.WARN)


def create_crds(logger):
    try:
        k8s_config.load_kube_config()
    except k8s_config.ConfigException:
        k8s_config.load_incluster_config()

    api_instance = k8s_client.ApiextensionsV1Api()
    for crd in [MonitorV1Beta1.crd, PspV1Beta1.crd, MaintenanceWindowV1Beta1.crd, AlertContactV1Beta1.crd]:
        try:
            api_instance.create_custom_resource_definition(crd)
            logger.info(f'CRD {crd.metadata.name} successfully created')
        except k8s_client.rest.ApiException as error:
            if error.status == 409:
                api_instance.patch_custom_resource_definition(
                    name=crd.metadata.name, body=crd)
                logger.debug(f'CRD {crd.metadata.name} successfully patched')
            else:
                logger.error(f'CRD {crd.metadata.name} failed to create')
                raise error


def init_uptimerobot_api(logger):
    global uptime_robot
    try:
        uptime_robot = uptimerobot.create_uptimerobot_api()
    except Exception as error:
        logger.error('failed to create UptimeRobot API')
        raise kopf.PermanentError(error)

def check_response(resp, logger, thing, action, id = None, jsonName = None):
    jsonName = jsonName if jsonName else thing.lower()
    if resp['stat'] == 'ok':
        if jsonName in resp:
            id = resp[jsonName]['id']
        logger.info(
            f'{thing} with ID {id} has been {action}d successfully')
    else:
        if resp['error']['type'] == 'not_found':
            logger.info(
                f'Could not {action} {thing} with ID {id} because does not exist.')
            return

        idDesc = f" {id}" if Id else ""
        raise kopf.PermanentError(
            f'failed to {action} {thing}{idDesc}: {resp["error"]}')

def create_monitor(namespace: str, name: str, spec: dict, logger):  
    request_dict = MonitorV1Beta1.spec_to_request_dict(namespace, name, spec)
    check_response(uptime_robot.new_monitor(**request_dict), logger, "monitor", "create", name)   

def update_monitor(namespace: str, name: str, spec: dict, logger, id): 
    request_dict = MonitorV1Beta1.spec_to_request_dict(namespace, name, spec)
    check_response(uptime_robot.edit_monitor(id, **request_dict), logger, "monitor", "update", id)

def delete_monitor(logger, id):
    check_response(uptime_robot.delete_monitor(id), logger, "monitor", "delete", id)

def create_psp(logger, **kwargs):
    resp = uptime_robot.new_psp(
        type='1',
        **{k:str(v) for k,v in kwargs.items()}
        )
    check_response(resp, logger, "PSP", "create")
    
def update_psp(logger, id, **kwargs):
    resp = uptime_robot.edit_psp(id, **{k:str(v) for k,v in kwargs.items()} )
    check_response(resp, logger, "PSP", "update")

def delete_psp(logger, id):
    check_response(uptime_robot.delete_psp(id), logger, "PSP", "delete")

def create_mw(logger, **kwargs):
    resp = uptime_robot.new_m_window(**{k:str(v) for k,v in kwargs.items()})
    check_response(resp, logger, "MW", "create", jsonName="mwindow")

def update_mw(logger, id, **kwargs):
    resp = uptime_robot.edit_m_window(id, **{k:str(v) for k,v in kwargs.items()})
    check_response(resp, logger, "MW", "update", id, "mwindow")

def delete_mw(logger, id):
    check_response(uptime_robot.delete_m_window(id), logger, "MW", "delete", id)

def create_ac(logger, **kwargs):
    resp = uptime_robot.new_alert_contact(**{k:str(v) for k,v in kwargs.items()})
    check_response(resp, logger, "alert contact", "delete", id, "alertcontact")

def update_ac(logger, id, **kwargs):
    resp = uptime_robot.edit_alert_contact(str(id), **{k:str(v) for k,v in kwargs.items()} )
    check_response(resp, logger, "alert contact", "update", id, "alert_contact")

def delete_ac(logger, id):
    check_response(uptime_robot.delete_alert_contact(str(id)), logger, "alert contact", "update", id)

def type_changed(diff: list):
    try:
        for entry in diff:
            if entry[0] == 'change' and entry[1][1] == 'type':
                return True
    except IndexError:
        return False
    return False

def get_status_value(status: dict, keyName, updateEvent, createEvent):
    return (status[updateEvent.__name__][keyName] if updateEvent.__name__ in status 
            else status[createEvent.__name__][keyName] if createEvent.__name__ in status 
            else -1 )

def get_identifier(status: dict):
    return get_status_value(status, MONITOR_ID_KEY, on_update, on_create)
    
def get_psp_identifier(status: dict):
    return get_status_value(status, PSP_ID_KEY, on_psp_update, on_psp_create)

def get_mw_identifier(status: dict):
    return get_status_value(status, MW_ID_KEY, on_mw_update, on_mw_create)

def get_ac_identifier(status: dict):
    return get_status_value(status, AC_ID_KEY, on_ac_update, on_ac_create)

@kopf.on.startup()
def startup(logger, **_):
    if config.DISABLE_INGRESS_HANDLING:
        logger.info('handling of Ingress resources has been disabled')

    global k8s
    k8s = K8s()
    init_uptimerobot_api(logger)
    create_crds(logger)

@kopf.on.create('networking.k8s.io', 'v1', 'ingresses')
def on_ingress_create(name: str, namespace: str, annotations: dict, spec: dict, logger, **_):
    logger.info(f"Creating monitors for new ingress {name}")
    create_or_update_crds(name, namespace, annotations, spec, logger)
    
@kopf.on.update('networking.k8s.io', 'v1', 'ingresses')
def on_ingress_update(name: str, namespace: str, annotations: dict, spec: dict, old: dict, logger, **_):
    logger.info(f"Updating monitors for ingress {name}")
    create_or_update_crds(name, namespace, annotations, spec, logger)

def create_or_update_crds(ingressName: str, namespace: str, annotations: dict, spec: dict, logger):
    def match_crd_to_rule(rule: dict, crd:dict):
        return generate_monitor_name(rule) == crd['metadata']['name'] 

    def match_crd_to_ingress(crd: dict):
        return ('ownerReferences' in crd['metadata']
            and crd['metadata']['ownerReferences'][0]['name'] == ingressName)
            
    def generate_monitor_name(rule: dict):
        host = rule['host']
        port = rule['port'] if 'port' in rule else ''
        path = rule['path'] if 'path' in rule else ''
        
        sha = hashlib.sha256()
        sha.update(f"{ingressName}{host}{path}{port}".encode())
        digest = sha.hexdigest()[:8]
        return f"{host}-{digest}"
        
    if config.DISABLE_INGRESS_HANDLING:
        logger.debug('handling of Ingress resources has been disabled')
        return

    monitor_prefix = f'{GROUP}/monitor.'
    monitor_spec = {k.replace(monitor_prefix, ''): v for k, v in annotations.items() if k.startswith(monitor_prefix)}

    rules = []
    for rule in spec['rules']:
        if 'host' not in rule:
            continue

        host = rule['host']
        # Filter out wildcard, unqualified, and excluded domains
        if host.startswith('*') or '.' not in host or host.endswith(config.EXCLUDED_DOMAINS):
            if host is not None:
                logger.info(f'Excluding rule for {host} as wildcard, unqualified, or excluded.')            
        else:
            rules.append(rule)

    crds = k8s.list_k8s_crd_obj(namespace)
    for crd in crds:   
        if match_crd_to_ingress(crd) and not any(match_crd_to_rule(rule, crd) for rule in rules):
            k8s.delete_k8s_crd_obj(MonitorV1Beta1, namespace, crd['metadata']['name'])    
            logger.info('deleted obsolete UptimeRobotMonitor object')

    for rule in rules:
        host = rule['host']

        if 'type' not in monitor_spec:
            logger.info(f"Type not specified. Defaulting to {config.DEFAULT_MONITOR_TYPE}")
            monitor_spec['type'] = config.DEFAULT_MONITOR_TYPE

        formatUrl(monitor_spec, host)
        monitor_name = generate_monitor_name(rule)
        monitor_body = MonitorV1Beta1.construct_k8s_ur_monitor_body(
            namespace, ingressName=monitor_name, **MonitorV1Beta1.annotations_to_spec_dict(monitor_spec))
        kopf.adopt(monitor_body)

        if any(match_crd_to_rule(rule, crd) for crd in crds):
            k8s.update_k8s_crd_obj_with_body(MonitorV1Beta1, namespace, monitor_name, monitor_body)
            logger.info(f'Updated UptimeRobotMonitor object for URL {host}')
        else:
            k8s.create_k8s_crd_obj_with_body(MonitorV1Beta1, namespace, monitor_body)
            logger.info(f'Created UptimeRobotMonitor object for URL {host}')

def formatUrl(monitor_body: dict, host):
    if 'url' in monitor_body and '://' in monitor_body['url']:
        return
    
    if monitor_body['type'] == 'HTTP':
        monitor_body['url'] = f"http://{host}"
    elif monitor_body['type'] in ['HTTPS', 'KEYWORD']:
        monitor_body['url'] = f"https://{host}"
    else:
        monitor_body['url'] = host

def set_crd_defaults(namespace: str, monitor_name: str, monitor_body: dict, logger):
    updated_body = {k:v for k,v in monitor_body.items()}
    # logger.info(f"Setting monitor defaults for {monitor_name}")
    
    formatUrl(updated_body, updated_body['url'])

    if 'customHttpHeaders' not in updated_body and config.DEFAULT_HEADERS != {}:
        logger.info('CustomHttpHeaders not set on monitor. Using user-define defaults.')
        updated_body['customHttpHeaders'] = config.DEFAULT_HEADERS

    k8s.update_k8s_crd_obj_with_body(MonitorV1Beta1, namespace, monitor_name, 
        MonitorV1Beta1.construct_k8s_ur_monitor_body(namespace, monitor_name, **updated_body))
    return updated_body

@kopf.on.create(GROUP, VERSION, PLURAL)
def on_create(namespace: str, name: str, spec: dict, logger, **_):
    logger.info(f"Monitor created: {name}")
    spec = set_crd_defaults(namespace, name, spec, logger)
    return {MONITOR_ID_KEY: create_monitor(namespace, name, spec, logger)}

@kopf.on.update(GROUP, VERSION, PLURAL)
def on_update(namespace: str, name: str, spec: dict, status: dict, diff: list, logger, **_):
    logger.info(f"Monitor updated: {name}")
    spec = set_crd_defaults(namespace, name, spec, logger)
    identifier = get_identifier(status)
    if identifier == -1:
        raise kopf.PermanentError(
            "was not able to determine the monitor ID for update") from error
    if type_changed(diff):
        logger.info('monitor type changed, need to delete and recreate')
        delete_monitor(logger, identifier)
        return {MONITOR_ID_KEY: create_monitor(namespace, name, spec, logger)}
    else:
        return {MONITOR_ID_KEY: update_monitor(namespace, name, spec, logger, identifier)}

    
@kopf.on.delete(GROUP, VERSION, PLURAL)
def on_delete(status: dict, logger, **_):
    identifier = get_identifier(status)
    if identifier == -1:
        raise kopf.PermanentError(
            "was not able to determine the monitor ID for deletion") from error
    try:
        delete_monitor(logger, identifier)
    except Exception as error:
        raise kopf.PermanentError(f"deleting monitor failed: {error}") from error

@kopf.on.create(GROUP, VERSION, PspV1Beta1.plural)
def on_psp_create(namespace: str, name: str, spec: dict, logger, **_):
    identifier = create_psp(
        logger,
        **PspV1Beta1.spec_to_request_dict(namespace, name, spec)
    )

    return {PSP_ID_KEY: identifier}

@kopf.on.update(GROUP, VERSION, PspV1Beta1.plural)
def on_psp_update(namespace: str, name: str, spec: dict, status: dict, logger, **_):
    identifier = get_psp_identifier(status)
    if identifier == -1:
        raise kopf.PermanentError(
            "was not able to determine the PSP ID for update") from error

    identifier = update_psp(
        logger,
        identifier,
        **PspV1Beta1.spec_to_request_dict(namespace, name, spec)
    )

    return {PSP_ID_KEY: identifier}

@kopf.on.delete(GROUP, VERSION, PspV1Beta1.plural)
def on_psp_delete(status: dict, logger, **_):
    identifier = get_psp_identifier(status)
    if identifier == -1:
        raise kopf.PermanentError(
            "was not able to determine the PSP ID for deletion") from error
    try:
        delete_psp(logger, identifier)
    except Exception as error:
        raise kopf.PermanentError(f"deleting PSP failed: {error}") from error

@kopf.on.create(GROUP, VERSION, MaintenanceWindowV1Beta1.plural)
def on_mw_create(name: str, spec: dict, logger, **_):
    identifier = create_mw(
        logger,
        **MaintenanceWindowV1Beta1.spec_to_request_dict(name, spec)
    )

    return {MW_ID_KEY: identifier}

@kopf.on.update(GROUP, VERSION, MaintenanceWindowV1Beta1.plural)
def on_mw_update(name: str, spec: dict, status: dict, logger, diff: dict, **_):
    identifier = get_mw_identifier(status)
    if identifier == -1:
        raise kopf.PermanentError(
            "was not able to determine the MW ID for update") from error

    update_payload = MaintenanceWindowV1Beta1.spec_to_request_dict(name, spec)

    if type_changed(diff):
        logger.info('maintenance window type changed, need to delete and recreate')
        delete_mw(logger, identifier)

        identifier = create_mw(
            logger,
            **update_payload
        )
    else:
        update_payload.pop('type', None) # update does not accept type parameter

        identifier = update_mw(
            logger,
            identifier,
            **update_payload
        )

    return {MW_ID_KEY: identifier}

@kopf.on.delete(GROUP, VERSION, MaintenanceWindowV1Beta1.plural)
def on_mw_delete(status: dict, logger, **_):
    identifier = get_mw_identifier(status)
    if identifier == -1:
        raise kopf.PermanentError(
            "was not able to determine the MW ID for deletion") from error
    try:
        delete_mw(logger, identifier)
    except Exception as error:
        raise kopf.PermanentError(f"deleting MW failed: {error}") from error

@kopf.on.create(GROUP, VERSION, AlertContactV1Beta1.plural)
def on_ac_create(name: str, spec: dict, logger, **_):
    identifier = create_ac(
        logger,
        **AlertContactV1Beta1.spec_to_request_dict(name, spec)
    )

    return {AC_ID_KEY: identifier}

@kopf.on.update(GROUP, VERSION, AlertContactV1Beta1.plural)
def on_ac_update(name: str, spec: dict, status: dict, logger, diff: dict, **_):
    identifier = get_ac_identifier(status)
    if identifier == -1:
        raise kopf.PermanentError(
            "was not able to determine the AC ID for update") from error

    update_payload = AlertContactV1Beta1.spec_to_request_dict(name, spec)

    if type_changed(diff) or spec['type'] != AlertContactType.WEB_HOOK.name:
        logger.info('alert contact type changed or is not of type WEB_HOOK, need to delete and recreate')
        delete_ac(logger, identifier)

        identifier = create_ac(
            logger,
            **update_payload
        )
    else:
        update_payload.pop('type', None) # update does not accept type parameter

        identifier = update_ac(
            logger,
            identifier,
            **update_payload
        )

    return {AC_ID_KEY: identifier}

@kopf.on.delete(GROUP, VERSION, AlertContactV1Beta1.plural)
def on_ac_delete(status: dict, logger, **_):
    identifier = get_ac_identifier(status)
    if identifier == -1:
        raise kopf.PermanentError(
            "was not able to determine the AC ID for deletion") from error
    try: 
        delete_ac(logger, identifier)
    except Exception as error:
        raise kopf.PermanentError(f"deleting AC failed: {error}") from error
