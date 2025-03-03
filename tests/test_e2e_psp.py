import base64
import kubernetes.client as k8s_client
import kubernetes.config as k8s_config
import sys

from ur_operator.config import Config
from ur_operator.handlers.common.uptimerobot import UptimeRobot

from .utils import namespace_handling, kopf_runner, create_opaque_secret, NAMESPACE, DEFAULT_WAIT_TIME

import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../ur_operator')))


from ur_operator.crds.psp import PspV1Beta1, PspSort
from ur_operator.handlers.common.k8s import K8s


k8s = K8s()
k8s_config.load_kube_config()
core_api = k8s_client.CoreV1Api()
uptime_robot = UptimeRobot(Config()).api


def create_k8s_ur_psp(namespace, name, wait_for_seconds=DEFAULT_WAIT_TIME, **spec):
<<<<<<< HEAD
    k8s.create_resource(PspV1Beta1, namespace, name, **spec)
=======
    k8s.create_obj(PspV1Beta1, namespace, name, **spec)
>>>>>>> 7e98f0b804dc5ff4ae1c76a84b313c4506b32e37
    time.sleep(wait_for_seconds)


def update_k8s_ur_psp(namespace, name, wait_for_seconds=DEFAULT_WAIT_TIME, **spec):
<<<<<<< HEAD
    k8s.update_resource(PspV1Beta1, namespace, name, **spec)
=======
    k8s.update_obj(PspV1Beta1, namespace, name, **spec)
>>>>>>> 7e98f0b804dc5ff4ae1c76a84b313c4506b32e37
    time.sleep(wait_for_seconds)


def delete_k8s_ur_psp(namespace, name, wait_for_seconds=DEFAULT_WAIT_TIME):
    k8s.delete_resource(PspV1Beta1, namespace, name)
    time.sleep(wait_for_seconds)


class TestDefaultOperator:
    def test_create_psp(self, kopf_runner, namespace_handling):
        name = 'foo'
        monitors = '0'
        password = 's3cr3t'
        sort = PspSort.STATUS_DOWN_UP_PAUSED

        create_k8s_ur_psp(NAMESPACE, name, monitors=monitors, password=password, sort=sort.name)

        psps = uptime_robot.get_psp()['psps']
        assert len(psps) == 1
        assert psps[0]['friendly_name'] == name
        assert psps[0]['monitors'] == 0
        assert psps[0]['sort'] == sort.value

    def test_create_psp_with_friendly_name(self, kopf_runner, namespace_handling):
        name = 'foo'
        friendly_name = 'bar'
        monitors = '0'

        create_k8s_ur_psp(NAMESPACE, name, friendlyName=friendly_name, monitors=monitors)

        psps = uptime_robot.get_psp()['psps']
        assert len(psps) == 1
        assert psps[0]['friendly_name'] == friendly_name
        assert psps[0]['monitors'] == 0

    def test_create_psp_with_hidden_url_links(self, kopf_runner, namespace_handling):
        name = 'foo'
        monitors = '0'
        hiddenUrlLinks = True

        create_k8s_ur_psp(NAMESPACE, name, monitors=monitors, hiddenUrlLinks=hiddenUrlLinks)

        psps = uptime_robot.get_psp()['psps']
        assert len(psps) == 1
        assert psps[0]['friendly_name'] == name
        assert psps[0]['monitors'] == 0

    def test_create_psp_with_password_secret(self, kopf_runner, namespace_handling):
        name = 'foo'
        monitors = '0'
        passwordSecretName = 'my-password-secret'
        passwordSecretValue = 's3cr3t'

        create_opaque_secret(NAMESPACE, passwordSecretName, {'password': base64.b64encode(passwordSecretValue.encode()).decode()})
        create_k8s_ur_psp(NAMESPACE, name, monitors=monitors, passwordSecret=passwordSecretName)

        psps = uptime_robot.get_psp()['psps']
        assert len(psps) == 1
        assert psps[0]['friendly_name'] == name
        assert psps[0]['monitors'] == 0

    def test_update_psp(self, kopf_runner, namespace_handling):
        name = 'foo'
        new_name = 'bar'
        monitors = '0'

        create_k8s_ur_psp(NAMESPACE, name, monitors=monitors)

        psps = uptime_robot.get_psp()['psps']
        assert len(psps) == 1
        assert psps[0]['friendly_name'] == name

        update_k8s_ur_psp(NAMESPACE, name, friendlyName=new_name)

        psps = uptime_robot.get_psp()['psps']
        assert len(psps) == 1
        assert psps[0]['friendly_name'] == new_name

    def test_delete_psp(self, kopf_runner, namespace_handling):
        name = 'foo'
        monitors = '0'

        create_k8s_ur_psp(NAMESPACE, name, monitors=monitors)

        psps = uptime_robot.get_psp()['psps']
        assert len(psps) == 1

        delete_k8s_ur_psp(NAMESPACE, name)

        psps = uptime_robot.get_psp()['psps']
        assert len(psps) == 0
