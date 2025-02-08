"""Base class for handlers"""
import kopf
from config import Config
from crds import BaseCrd
from api import K8s, UptimeRobot


class BaseHandler():
    """Base class for handlers"""

    def __init__(self, ur: UptimeRobot, crd: type[BaseCrd],
                 create_event_name, update_event_name, status_key):
        self.crd = crd
        self.config = Config()
        self.k8s = K8s(crd)
        self.id_key = status_key
        self.create_event_name = create_event_name
        self.update_event_name = update_event_name
        self.uptime_robot = ur

    def get_identifier(self, status: dict):
        """Retrieve the status value for a given resource, 
        based on this handler's specified id key."""
        if self.update_event_name in status:
            return str(status[self.update_event_name][self.id_key])
        if self.create_event_name in status:
            return status[self.create_event_name][self.id_key]
        raise kopf.PermanentError(
            f"was not able to determine the {self.id_key}!")

    def build_request(self, name, spec: dict):
        """Create an UptimeRobot API request for this handler's CRD"""
        return self.crd.spec_to_request_dict(name, spec)


def format_url(monitor_body: dict, host):
    """Prefix a given monitor's URL with HTTP:// or HTTPS:// based on its type,
    unless the type is PING."""
    if 'url' in monitor_body and '://' in monitor_body['url']:
        return

    if monitor_body['type'] == 'HTTP':
        monitor_body['url'] = f"http://{host}"
    elif monitor_body['type'] in ['HTTPS', 'KEYWORD']:
        monitor_body['url'] = f"https://{host}"
    else:
        monitor_body['url'] = host


def type_changed(diff: dict | list):
    """Check if a resource's type was changed in an update"""
    try:
        for entry in diff:
            if entry[0] == 'change' and entry[1][1] == 'type':
                return True
    except IndexError:
        return False
    return False
