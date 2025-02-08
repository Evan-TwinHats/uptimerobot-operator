"""Functions to create kopf decoractors based on a CRD class"""
from crds import BaseCrd
import kopf.on

# pylint: disable=missing-function-docstring


def create(crd: type[BaseCrd]) -> kopf.on.ChangingDecorator:
    return kopf.on.create(crd.group(), crd.version(), crd.plural())


def update(crd: type[BaseCrd]) -> kopf.on.ChangingDecorator:
    return kopf.on.update(crd.group(), crd.version(), crd.plural())


def delete(crd: type[BaseCrd]) -> kopf.on.ChangingDecorator:
    return kopf.on.delete(crd.group(), crd.version(), crd.plural())
# pylint: enable=missing-function-docstring
