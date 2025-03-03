import pytest
import kubernetes.client as k8s_client
import kubernetes.config as k8s_config
import sys

from ur_operator.config import Config
from ur_operator.handlers.common.uptimerobot import UptimeRobot

from .utils import namespace_handling, kopf_runner, NAMESPACE, DEFAULT_WAIT_TIME

import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../ur_operator')))


from ur_operator.crds.maintenance_window import MaintenanceWindowV1Beta1, MaintenanceWindowType
from ur_operator.handlers.common.k8s import K8s


k8s = K8s()
k8s_config.load_kube_config()
core_api = k8s_client.CoreV1Api()
uptime_robot = UptimeRobot(Config()).api


def create_k8s_ur_mw(namespace, name, wait_for_seconds=DEFAULT_WAIT_TIME, **spec):
<<<<<<< HEAD
    k8s.create_resource(MaintenanceWindowV1Beta1, namespace, name, **spec)
=======
    k8s.create_obj(MaintenanceWindowV1Beta1, namespace, name, **spec)
>>>>>>> 7e98f0b804dc5ff4ae1c76a84b313c4506b32e37
    time.sleep(wait_for_seconds)


def update_k8s_ur_mw(namespace, name, wait_for_seconds=DEFAULT_WAIT_TIME, **spec):
<<<<<<< HEAD
    k8s.update_resource(MaintenanceWindowV1Beta1, namespace, name, **spec)
=======
    k8s.update_obj(MaintenanceWindowV1Beta1, namespace, name, **spec)
>>>>>>> 7e98f0b804dc5ff4ae1c76a84b313c4506b32e37
    time.sleep(wait_for_seconds)


def delete_k8s_ur_mw(namespace, name, wait_for_seconds=DEFAULT_WAIT_TIME):
    k8s.delete_resource(MaintenanceWindowV1Beta1, namespace, name)
    time.sleep(wait_for_seconds)


class TestDefaultOperator:
    def test_create_once_mw(self, kopf_runner, namespace_handling):
        name = 'foo'
        mw_type = MaintenanceWindowType.ONCE
        start_time = str(int(time.time()) + 60)
        duration = 30

        create_k8s_ur_mw(NAMESPACE, name, type=mw_type.name, startTime=start_time, duration=duration)

        mws = uptime_robot.get_m_window()['mwindows']
        assert len(mws) == 1
        assert mws[0]['friendly_name'] == name
        assert mws[0]['type'] == mw_type.value
        assert mws[0]['start_time'] == int(start_time)
        assert mws[0]['duration'] == duration

    def test_create_daily_mw(self, kopf_runner, namespace_handling):
        name = 'foo'
        mw_type = MaintenanceWindowType.DAILY
        start_time = '06:30'
        duration = 30

        create_k8s_ur_mw(NAMESPACE, name, type=mw_type.name, startTime=start_time, duration=duration)

        mws = uptime_robot.get_m_window()['mwindows']
        assert len(mws) == 1
        assert mws[0]['friendly_name'] == name
        assert mws[0]['type'] == mw_type.value
        assert mws[0]['start_time'] == start_time
        assert mws[0]['duration'] == duration

    def test_create_weekly_mw(self, kopf_runner, namespace_handling):
        name = 'foo'
        mw_type = MaintenanceWindowType.WEEKLY
        start_time = '06:30'
        duration = 30
        value = '2-4-5'

        create_k8s_ur_mw(NAMESPACE, name, type=mw_type.name, startTime=start_time, duration=duration, value=value)

        mws = uptime_robot.get_m_window()['mwindows']
        assert len(mws) == 1
        assert mws[0]['friendly_name'] == name
        assert mws[0]['type'] == mw_type.value
        assert mws[0]['start_time'] == start_time
        assert mws[0]['duration'] == duration
        assert mws[0]['value'] == value.replace('-', ',')

    def test_create_monthly_mw(self, kopf_runner, namespace_handling):
        name = 'foo'
        mw_type = MaintenanceWindowType.MONTHLY
        start_time = '06:30'
        duration = 30
        value = '1-11-21-31'

        create_k8s_ur_mw(NAMESPACE, name, type=mw_type.name, startTime=start_time, duration=duration, value=value)

        mws = uptime_robot.get_m_window()['mwindows']
        assert len(mws) == 1
        assert mws[0]['friendly_name'] == name
        assert mws[0]['type'] == mw_type.value
        assert mws[0]['start_time'] == start_time
        assert mws[0]['duration'] == duration
        assert mws[0]['value'] == value.replace('-', ',')

    def test_create_mw_with_friendly_name(self, kopf_runner, namespace_handling):
        name = 'foo'
        friendly_name = 'bar'
        mw_type = MaintenanceWindowType.ONCE
        start_time = str(int(time.time()) + 60)
        duration = 30

        create_k8s_ur_mw(NAMESPACE, name, type=mw_type.name, startTime=start_time, duration=duration, friendlyName=friendly_name)

        mws = uptime_robot.get_m_window()['mwindows']
        assert len(mws) == 1
        assert mws[0]['friendly_name'] == friendly_name

    def test_update_mw(self, kopf_runner, namespace_handling):
        name = 'foo'
        new_name = 'bar'
        mw_type = MaintenanceWindowType.ONCE
        start_time = str(int(time.time()) + 60)
        duration = 30
        new_duration = 30

        create_k8s_ur_mw(NAMESPACE, name, type=mw_type.name, startTime=start_time, duration=duration)

        mws = uptime_robot.get_m_window()['mwindows']
        assert len(mws) == 1
        assert mws[0]['friendly_name'] == name
        assert mws[0]['duration'] == duration

        update_k8s_ur_mw(NAMESPACE, name, friendlyName=new_name, duration=new_duration)

        mws = uptime_robot.get_m_window()['mwindows']
        assert len(mws) == 1
        assert mws[0]['friendly_name'] == new_name
        assert mws[0]['duration'] == new_duration

    def test_update_mw_change_type(self, kopf_runner, namespace_handling):
        name = 'foo'
        mw_type = MaintenanceWindowType.ONCE
        new_mw_type = MaintenanceWindowType.DAILY
        start_time = str(int(time.time()) + 60)
        new_start_time = '10:00'
        duration = 30

        create_k8s_ur_mw(NAMESPACE, name, type=mw_type.name, startTime=start_time, duration=duration)

        mws = uptime_robot.get_m_window()['mwindows']
        assert len(mws) == 1
        assert mws[0]['type'] == mw_type.value
        assert mws[0]['start_time'] == int(start_time)

        update_k8s_ur_mw(NAMESPACE, name, type=new_mw_type.name, startTime=new_start_time)

        mws = uptime_robot.get_m_window()['mwindows']
        assert len(mws) == 1
        assert mws[0]['type'] == new_mw_type.value
        assert mws[0]['start_time'] == new_start_time

    def test_delete_mw(self, kopf_runner, namespace_handling):
        name = 'foo'
        mw_type = MaintenanceWindowType.ONCE
        start_time = str(int(time.time()) + 60)
        duration = 30

        create_k8s_ur_mw(NAMESPACE, name, type=mw_type.name, startTime=start_time, duration=duration)

        mws = uptime_robot.get_m_window()['mwindows']
        assert len(mws) == 1

        delete_k8s_ur_mw(NAMESPACE, name)

        mws = uptime_robot.get_m_window()['mwindows']
        assert len(mws) == 0
