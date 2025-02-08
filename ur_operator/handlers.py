"""Main operator logic and handlers"""
import logging
from kopf.on import startup as on_startup
from kopf import PermanentError
from config import Config
from crds import ALL_CRDS, CustomResourceDefinition, AlertContactV1Beta1
from crds import MaintenanceWindowV1Beta1, MonitorV1Beta1, PspV1Beta1, IngressV1, make_spec
from kubernetes.client.rest import ApiException
from handlers import MonitorHandler, AlertContactHandler
from handlers import MaintananceWindowHandler, PSPHandler, IngressHandler
from api import UptimeRobot, K8s, on

ur: UptimeRobot
mon_handler: MonitorHandler
ac_handler: AlertContactHandler
ingress_handler: IngressHandler
mw_handler: MaintananceWindowHandler
psp_handler: PSPHandler

# disable liveness check request logs
logging.getLogger('aiohttp.access').setLevel(logging.WARN)


def __create_crds(logger):
    k8s = K8s(CustomResourceDefinition)

    for crd in ALL_CRDS:
        name = f'{crd.plural()}.{crd.group()}'
        spec = make_spec(crd)
        # logger.info(f"Spec for CRD {name}: {spec}")
        try:
            k8s.create_resource(None, name, spec)
            logger.info(f'CRD {name} successfully created')
        except ApiException as error:
            if error.status == 409:
                k8s.update_resource(None, name, spec)
                logger.debug(f'CRD {name} successfully patched')
            else:
                logger.error(f'CRD {name} failed to create')
                raise error


@on_startup()
def __startup(logger, **_):
    global ur, mon_handler, ac_handler, mw_handler, ingress_handler, psp_handler
    config = Config()

    if config.DISABLE_INGRESS_HANDLING:
        logger.info('handling of Ingress resources has been disabled')

    try:
        ur = UptimeRobot(config)
    except Exception as error:
        logger.error('failed to create UptimeRobot API')
        raise PermanentError(error) from error

    __create_crds(logger)
    psp_handler = PSPHandler(ur,
                             on_create_psp.__name__,
                             on_update_psp.__name__)
    mon_handler = MonitorHandler(ur,
                                 on_create_mon.__name__,
                                 on_update_mon.__name__)
    ac_handler = AlertContactHandler(ur,
                                     on_create_ac.__name__,
                                     on_update_ac.__name__)
    ingress_handler = IngressHandler(ur,
                                     on_create_ingress.__name__,
                                     on_update_ingress.__name__)
    mw_handler = MaintananceWindowHandler(ur,
                                          on_create_mw.__name__,
                                          on_update_mw.__name__)

# pylint: disable=missing-function-docstring


@on.create(IngressV1)
def on_create_ingress(name: str, namespace: str, annotations: dict, spec: dict, logger, **_):
    return ingress_handler.on_create(name, namespace, annotations, spec, logger)


@on.update(IngressV1)
def on_update_ingress(name: str, namespace: str, annotations: dict, spec: dict, logger, **_):
    return ingress_handler.on_update(name, namespace, annotations, spec, logger)


@on.create(AlertContactV1Beta1)
def on_create_ac(name: str, spec: dict, logger, **_):
    return ac_handler.on_create(name, spec, logger)


@on.update(AlertContactV1Beta1)
def on_update_ac(name: str, spec: dict, status: dict, logger, diff, **_):
    return ac_handler.on_update(name, spec, status, logger, diff)


@on.delete(AlertContactV1Beta1)
def on_delete_ac(status: dict, logger, **_):
    return ac_handler.on_delete(status, logger)


@on.create(MaintenanceWindowV1Beta1)
def on_create_mw(name: str, spec: dict, logger, **_):
    return mw_handler.on_create(name, spec, logger)


@on.update(MaintenanceWindowV1Beta1)
def on_update_mw(name: str, spec: dict, status: dict, logger, diff, **_):
    return mw_handler.on_update(name, spec, status, logger, diff)


@on.delete(MaintenanceWindowV1Beta1)
def on_delete_mw(status: dict, logger, **_):
    return mw_handler.on_delete(status, logger)


@on.create(MonitorV1Beta1)
def on_create_mon(spec, namespace: str, name: str, logger, **_):
    return mon_handler.on_create(namespace, name, spec, logger)


@on.update(MonitorV1Beta1)
def on_update_mon(namespace: str, name: str, spec: dict, status: dict, logger, diff, **_):
    return mon_handler.on_update(namespace, name, spec, status, diff, logger)


@on.delete(MonitorV1Beta1)
def on_delete_mon(status: dict, logger, **_):
    mon_handler.on_delete(status, logger)


@on.create(PspV1Beta1)
def on_create_psp(namespace: str, name: str, spec: dict, logger, **_):
    return psp_handler.on_create(namespace, name, spec, logger)


@on.update(PspV1Beta1)
def on_update_psp(namespace: str, name: str, spec: dict, status, logger, **_):
    return psp_handler.on_update(namespace, name, spec, status, logger)


@on.delete(PspV1Beta1)
def on_delete_psp(status, logger):
    return psp_handler.on_delete(status, logger)
# pylint: disable=missing-function-docstring
