def check_response(resp, logger, thing, action, id = None, jsonName = None):
    jsonName = jsonName if jsonName else thing.lower()
    if resp['stat'] == 'ok':
        if jsonName in resp:
            id = resp[jsonName]['id']
        logger.info(
            f'{thing} with ID {id} has been {action}d successfully')
    else:
        if resp['error']['type'] == 'not_found':
            logger.info(
                f'Could not {action} {thing} with ID {id} because does not exist.')
            return

        idDesc = f" {id}" if Id else ""
        raise kopf.PermanentError(
            f'failed to {action} {thing}{idDesc}: {resp["error"]}')

def stringify_values(props):
    return {k:str(v) for k,v in props.items()}

def get_status_value(status: dict, keyName, updateEvent, createEvent):
    return str(status[updateEvent.__name__][keyName] if updateEvent.__name__ in status 
            else status[createEvent.__name__][keyName] if createEvent.__name__ in status 
            else -1 )
    
def formatUrl(monitor_body: dict, host):
    if 'url' in monitor_body and '://' in monitor_body['url']:
        return
    
    if monitor_body['type'] == 'HTTP':
        monitor_body['url'] = f"http://{host}"
    elif monitor_body['type'] in ['HTTPS', 'KEYWORD']:
        monitor_body['url'] = f"https://{host}"
    else:
        monitor_body['url'] = host


def type_changed(diff: list):
    try:
        for entry in diff:
            if entry[0] == 'change' and entry[1][1] == 'type':
                return True
    except IndexError:
        return False
    return False
