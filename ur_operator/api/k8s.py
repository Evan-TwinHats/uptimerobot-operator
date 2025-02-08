"""API client for K8s"""
import logging
import base64
import time

import kopf
import kubernetes.config as k8s_config
from kubernetes.client import CustomObjectsApi, CoreV1Api, ApiClient
from kubernetes.dynamic.client import DynamicClient
from kubernetes.dynamic.exceptions import ResourceNotFoundError
from crds import BaseCrd, GROUP


class K8s:
    """API client for K8s"""

    def __init__(self, crd: type[BaseCrd]):
        self.crd = crd
        try:
            k8s_config.load_kube_config()
        except k8s_config.ConfigException:
            try:
                k8s_config.load_incluster_config()
            except k8s_config.ConfigException as error:
                logging.error(
                    "Failed to load kube and incluster config, giving up...")
                raise error

        client = DynamicClient(ApiClient())
        self.core_api = CoreV1Api()
        self.custom_objects_api = CustomObjectsApi()
        try:
            self.api = client.resources.get(
                api_version=f'{crd.group()}/{crd.version()}', kind=crd.kind())
        except ResourceNotFoundError:
            # Need to wait a sec for the discovery layer to get updated
            time.sleep(2)
        self.api = client.resources.get(
            api_version=f'{crd.group()}/{crd.version()}', kind=crd.kind())

    def create_body(self, namespace, name, spec, adopt):
        """Create a K8s resource body for the given name, namespace, and spec 
        with the proper apiVersion and kind retrieved from the CRD for this K8s instance."""
        body = {
            'apiVersion': f'{self.crd.group()}/{self.crd.version()}',
            'kind': self.crd.kind(),
            'metadata': {'name': name, 'namespace': namespace},
            'spec': spec
        }
        if adopt:
            kopf.adopt(body)

        return body

    def update_resource(self, namespace, name, spec, adopt=False):
        """Update a K8s resource"""
        body = self.create_body(namespace, name, spec, adopt)
        return self.api.patch(body=body, content_type="application/merge-patch+json")

    def create_resource(self, namespace, name, spec, adopt=False):
        """Create a K8s resource"""
        body = self.create_body(namespace, name, spec, adopt)
        return self.api.create(body)

    def list_resource(self, namespace):
        """List this K8s instance's CRDs in a given namespace"""
        return self.custom_objects_api.list_namespaced_custom_object(
            group=GROUP,
            version=self.crd.version(),
            plural=self.crd.plural(),
            namespace=namespace
        )['items']

    def delete_resource(self, namespace, name):
        """Delete a K8s resource"""
        self.custom_objects_api.delete_namespaced_custom_object(
            group=GROUP,
            version=self.crd.version(),
            plural=self.crd.plural(),
            namespace=namespace,
            name=name,
        )

    def get_secret(self, namespace, name) -> dict[str, str]:
        """Retrieve the decoded data from a K8s secret"""
        secret = self.core_api.read_namespaced_secret(name, namespace)
        return {k: base64.b64decode(v).decode() for k, v in secret.data}
