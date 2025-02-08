"""API clients for K8s and UptimeRobot. 
Also contains decorator functions that create kopf decorators. """
from .k8s import K8s
from .uptimerobot import UptimeRobot
from .on import create, update, delete
