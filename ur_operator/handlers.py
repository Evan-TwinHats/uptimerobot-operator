import logging
import uptimerobot 
import kopf
import kubernetes.config as k8s_config
import kubernetes.client as k8s_client
from crds.alert_contact import AlertContactV1Beta1
from crds.maintenance_window import MaintenanceWindowV1Beta1


from k8s import K8s
from config import Config
from handlers import ingress, alert_contact, maintanance_window
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

@kopf.on.startup()
def startup(logger, **_):
    if config.DISABLE_INGRESS_HANDLING:
        logger.info('handling of Ingress resources has been disabled')

    global k8s
    k8s = K8s()
    init_uptimerobot_api(logger)
    create_crds(logger)

@kopf.on.create('networking.k8s.io', 'v1', 'ingresses')
def on_create_ingress(name: str, namespace: str, annotations: dict, spec: dict, logger, **_):
    ingress.on_create(config, name, namespace, annotations, spec, logger)

@kopf.on.update_ingress('networking.k8s.io', 'v1', 'ingresses')
def on_update(name: str, namespace: str, annotations: dict, spec: dict, old: dict, logger, **_):
    ingress.on_update(config, name, namespace, annotations, spec, logger)


@kopf.on.create(GROUP, AlertContactV1Beta1.version, AlertContactV1Beta1.plural)
def on_create_ac(name: str, spec: dict, logger, **_):
    alert_contact.on_create(name, spec, logger, AlertContactV1Beta1.spec_to_request_dict)

@kopf.on.update(GROUP, AlertContactV1Beta1.version, AlertContactV1Beta1.plural)
def on_update_ac(name: str, spec: dict, status: dict, logger, diff: dict, **_):
    alert_contact.on_update(name, spec, status, logger, diff, AlertContactV1Beta1.spec_to_request_dict)

@kopf.on.delete_ac(GROUP, AlertContactV1Beta1.version, AlertContactV1Beta1.plural)
def on_delete(status: dict, logger, **_):
    alert_contact.on_delete(status, logger)


@kopf.on.create(GROUP, MaintenanceWindowV1Beta1.version, MaintenanceWindowV1Beta1.plural)
def on_create_mw(name: str, spec: dict, logger, **_):
    maintanance_window.on_create(name, spec, logger, MaintenanceWindowV1Beta1.spec_to_request_dict)

@kopf.on.update(GROUP, MaintenanceWindowV1Beta1.version, MaintenanceWindowV1Beta1.plural)
def on_update_mw(name: str, spec: dict, status: dict, logger, diff: dict, **_):
    maintanance_window.on_update(name, spec, status, logger, MaintenanceWindowV1Beta1.spec_to_request_dict)

@kopf.on.delete(GROUP, MaintenanceWindowV1Beta1.version, MaintenanceWindowV1Beta1.plural)
def on_delete_mw(status: dict, logger, **_):
    maintanance_window.on_delete(status, logger)