import k8s
import kopf

def on_create(config, name: str, namespace: str, annotations: dict, spec: dict, logger):
    logger.info(f"Creating monitors for new ingress {name}")
    create_or_update_crds(config, name, namespace, annotations, spec, logger)
    
def on_update(config, name: str, namespace: str, annotations: dict, spec: dict, old: dict, logger):
    logger.info(f"Updating monitors for ingress {name}")
    create_or_update_crds(config, name, namespace, annotations, spec, logger)

def create_or_update_crds(config, ingressName: str, namespace: str, annotations: dict, spec: dict, logger):
    def match_crd_to_rule(rule: dict, crd:dict):
        return generate_monitor_name(rule) == crd['metadata']['name'] 

    def match_crd_to_ingress(crd: dict):
        return ('ownerReferences' in crd['metadata']
            and crd['metadata']['ownerReferences'][0]['name'] == ingressName)
            
    def generate_monitor_name(rule: dict):
        host = rule['host']
        port = rule['port'] if 'port' in rule else ''
        path = rule['path'] if 'path' in rule else ''
        
        sha = hashlib.sha256()
        sha.update(f"{ingressName}{host}{path}{port}".encode())
        digest = sha.hexdigest()[:8]
        return f"{host}-{digest}"
        
    if config.DISABLE_INGRESS_HANDLING:
        logger.debug('handling of Ingress resources has been disabled')
        return

    monitor_prefix = f'{config.GROUP}/monitor.'
    monitor_spec = {k.replace(monitor_prefix, ''): v for k, v in annotations.items() if k.startswith(monitor_prefix)}

    rules = []
    for rule in spec['rules']:
        if 'host' not in rule:
            continue

        host = rule['host']

        # Filter out wildcard, unqualified, and excluded domains
        if host.startswith('*') or '.' not in host or host.endswith(config.EXCLUDED_DOMAINS):
            if host is not None:
                logger.info(f'Excluding rule for {host} as wildcard, unqualified, or excluded.')            
        else:
            rules.append(rule)

    crds = k8s.list_k8s_crd_obj(namespace)
    for crd in crds:   
        if match_crd_to_ingress(crd) and not any(match_crd_to_rule(rule, crd) for rule in rules):
            k8s.delete_k8s_crd_obj(MonitorV1Beta1, namespace, crd['metadata']['name'])    
            logger.info('deleted obsolete UptimeRobotMonitor object')

    for rule in rules:
        host = rule['host']

        if 'type' not in monitor_spec:
            logger.info(f"Type not specified. Defaulting to {config.DEFAULT_MONITOR_TYPE}")
            monitor_spec['type'] = config.DEFAULT_MONITOR_TYPE

        formatUrl(monitor_spec, host)
        monitor_name = generate_monitor_name(rule)
        monitor_body = MonitorV1Beta1.construct_k8s_ur_monitor_body(
            namespace, ingressName=monitor_name, **MonitorV1Beta1.annotations_to_spec_dict(monitor_spec))
        kopf.adopt(monitor_body)

        if any(match_crd_to_rule(rule, crd) for crd in crds):
            k8s.update_k8s_crd_obj_with_body(MonitorV1Beta1, namespace, monitor_name, monitor_body)
            logger.info(f'Updated UptimeRobotMonitor object for URL {host}')
        else:
            k8s.create_k8s_crd_obj_with_body(MonitorV1Beta1, namespace, monitor_body)
            logger.info(f'Created UptimeRobotMonitor object for URL {host}')

