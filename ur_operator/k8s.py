import logging
import json

import kubernetes.config as k8s_config
import kubernetes.client as k8s_client

from crds import constants

class K8s:
    def __init__(self):
        try:
            k8s_config.load_kube_config()
        except k8s_config.ConfigException:
            k8s_config.load_incluster_config()
        except k8s_config.ConfigException as error:
            logging.error("Failed to load kube and incluster config, giving up...")
            raise error

        self.custom_objects_api = k8s_client.CustomObjectsApi()
        self.core_api = k8s_client.CoreV1Api()

    def create_k8s_crd_obj_with_body(self, crd, namespace, body):
        return self.custom_objects_api.create_namespaced_custom_object(
            group=constants.GROUP,
            version=constants.VERSION,
            namespace=namespace,
            plural=constants.PLURAL,
            body=body
        )

    def update_k8s_crd_obj_with_body(self, crd, namespace, name, body):
        return self.custom_objects_api.patch_namespaced_custom_object(
            group=constants.GROUP,
            version=constants.VERSION,
            plural=constants.PLURAL,
            namespace=namespace,
            name=name,
            body=body
        )

    def create_k8s_crd_obj(self, crd, namespace, name, **spec):
        return self.create_k8s_crd_obj_with_body(
            crd,
            namespace,
            {
                'apiVersion': f'{constants.GROUP}/{constants.VERSION}',
                'kind': crd.kind,
                'metadata': {'name': name, 'namespace': namespace},
                'spec': spec
            }
        )

    def update_k8s_crd_obj(self, crd, namespace, name, **spec):
        return self.update_k8s_crd_obj_with_body(
            crd,
            namespace,
            name,
            {
                'spec': spec
            }
        )

    def list_k8s_crd_obj(self, namespace):
        return self.custom_objects_api.list_namespaced_custom_object(
            group=constants.GROUP,
            version=constants.VERSION,
            plural=constants.PLURAL,
            namespace=namespace
        )['items']

    def delete_k8s_crd_obj(self, crd, namespace, name):
        self.custom_objects_api.delete_namespaced_custom_object(
            group=constants.GROUP,
            version=constants.VERSION,
            plural=constants.PLURAL,
            namespace=namespace,
            name=name,
        )

    def get_secret(self, namespace, name):
        return self.core_api.read_namespaced_secret(name, namespace)
