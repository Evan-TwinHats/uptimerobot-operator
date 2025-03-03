from ur_operator.handlers.common.k8s import K8s
from ur_operator.crds.alert_contact import AlertContactV1Beta1, AlertContactType
from ur_operator.handlers.common.uptimerobot import UptimeRobot
import pytest
import kubernetes.client as k8s_client
import kubernetes.config as k8s_config
import sys

from ur_operator.config import Config

from .utils import NAMESPACE, DEFAULT_WAIT_TIME

import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../ur_operator')))


k8s = K8s()
k8s_config.load_kube_config()
core_api = k8s_client.CoreV1Api()
uptime_robot = UptimeRobot(Config()).api


def create_k8s_ur_ac(namespace, name, wait_for_seconds=DEFAULT_WAIT_TIME, **spec):
<<<<<<< HEAD
    k8s.create_resource(AlertContactV1Beta1, namespace, name, **spec)
=======
    k8s.create_obj(AlertContactV1Beta1, namespace, name, **spec)
>>>>>>> 7e98f0b804dc5ff4ae1c76a84b313c4506b32e37
    time.sleep(wait_for_seconds)


def update_k8s_ur_ac(namespace, name, wait_for_seconds=DEFAULT_WAIT_TIME, **spec):
<<<<<<< HEAD
    k8s.update_resource(AlertContactV1Beta1, namespace, name, **spec)
=======
    k8s.update_obj(AlertContactV1Beta1, namespace, name, **spec)
>>>>>>> 7e98f0b804dc5ff4ae1c76a84b313c4506b32e37
    time.sleep(wait_for_seconds)


def delete_k8s_ur_ac(namespace, name, wait_for_seconds=DEFAULT_WAIT_TIME):
    k8s.delete_resource(AlertContactV1Beta1, namespace, name)
    time.sleep(wait_for_seconds)


class TestDefaultOperator:
    def test_create_email_ac(self, kopf_runner, namespace_handling):
        name = 'foo'
        ac_type = AlertContactType.EMAIL
        value = 'foo@bar.com'

        create_k8s_ur_ac(NAMESPACE, name, type=ac_type.name, value=value)

        acs = uptime_robot.get_alert_contacts()['alert_contacts']
        assert len(acs) == 2
        assert acs[1]['friendly_name'] == name
        assert acs[1]['type'] == ac_type.value
        assert acs[1]['value'] == value

    @pytest.mark.skip(reason='needs fixing')
    def test_create_twitter_ac(self, kopf_runner, namespace_handling):
        name = 'foo'
        ac_type = AlertContactType.TWITTER_DM
        value = '__brennerm'

        create_k8s_ur_ac(NAMESPACE, name, type=ac_type.name, value=value)

        acs = uptime_robot.get_alert_contacts()['alert_contacts']
        assert len(acs) == 2
        assert acs[1]['friendly_name'] == name
        assert acs[1]['type'] == ac_type.value
        assert acs[1]['value'] == value

    def test_create_webhook_ac(self, kopf_runner, namespace_handling):
        name = 'foo'
        ac_type = AlertContactType.WEB_HOOK
        value = 'https://brennerm.github.io?'

        create_k8s_ur_ac(NAMESPACE, name, type=ac_type.name, value=value)

        acs = uptime_robot.get_alert_contacts()['alert_contacts']
        assert len(acs) == 2
        assert acs[1]['friendly_name'] == name
        assert acs[1]['type'] == ac_type.value
        assert acs[1]['value'] == value

    def test_create_mw_with_friendly_name(self, kopf_runner, namespace_handling):
        name = 'foo'
        friendly_name = 'bar'
        ac_type = AlertContactType.EMAIL
        value = 'foo@bar.com'

        create_k8s_ur_ac(NAMESPACE, name, type=ac_type.name,
                         value=value, friendlyName=friendly_name)

        acs = uptime_robot.get_alert_contacts()['alert_contacts']
        assert len(acs) == 2
        assert acs[1]['friendly_name'] == friendly_name
        assert acs[1]['type'] == ac_type.value
        assert acs[1]['value'] == value

    def test_update_ac_change_mail(self, kopf_runner, namespace_handling):
        name = 'foo'
        new_name = 'bar'
        ac_type = AlertContactType.EMAIL
        value = 'foo@bar.com'
        new_value = 'bar@foo.com'

        create_k8s_ur_ac(NAMESPACE, name, type=ac_type.name, value=value)

        acs = uptime_robot.get_alert_contacts()['alert_contacts']
        assert len(acs) == 2
        assert acs[1]['friendly_name'] == name
        assert acs[1]['value'] == value

        update_k8s_ur_ac(
            NAMESPACE, name, friendlyName=new_name, value=new_value)

        acs = uptime_robot.get_alert_contacts()['alert_contacts']
        assert len(acs) == 2
        assert acs[1]['friendly_name'] == new_name
        assert acs[1]['value'] == new_value

    def test_update_ac_change_webhook_url(self, kopf_runner, namespace_handling):
        name = 'foo'
        ac_type = AlertContactType.WEB_HOOK
        value = 'https://brennerm.github.io?'
        new_value = 'https://brennerm.github.com?'

        create_k8s_ur_ac(NAMESPACE, name, type=ac_type.name, value=value)

        acs = uptime_robot.get_alert_contacts()['alert_contacts']
        assert len(acs) == 2
        assert acs[1]['value'] == value

        update_k8s_ur_ac(NAMESPACE, name, value=new_value)

        acs = uptime_robot.get_alert_contacts()['alert_contacts']
        assert len(acs) == 2
        assert acs[1]['value'] == new_value

    def test_update_ac_change_type(self, kopf_runner, namespace_handling):
        name = 'foo'
        ac_type = AlertContactType.EMAIL
        new_ac_type = AlertContactType.WEB_HOOK
        value = 'foo@bar.com'
        new_value = 'https://brennerm.github.com?'

        create_k8s_ur_ac(NAMESPACE, name, type=ac_type.name, value=value)

        acs = uptime_robot.get_alert_contacts()['alert_contacts']
        assert len(acs) == 2
        assert acs[1]['type'] == ac_type.value
        assert acs[1]['value'] == value

        update_k8s_ur_ac(
            NAMESPACE, name, type=new_ac_type.name, value=new_value)

        acs = uptime_robot.get_alert_contacts()['alert_contacts']
        assert len(acs) == 2
        assert acs[1]['type'] == new_ac_type.value
        assert acs[1]['value'] == new_value

    def test_delete_ac(self, kopf_runner, namespace_handling):
        name = 'foo'
        ac_type = AlertContactType.EMAIL
        value = 'foo@bar.com'

        create_k8s_ur_ac(NAMESPACE, name, type=ac_type.name, value=value)

        acs = uptime_robot.get_alert_contacts()['alert_contacts']
        assert len(acs) == 2

        delete_k8s_ur_ac(NAMESPACE, name)

        acs = uptime_robot.get_alert_contacts()['alert_contacts']
        assert len(acs) == 1
