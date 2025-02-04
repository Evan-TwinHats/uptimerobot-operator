import os
import json

class Config:
    @property
    def DISABLE_INGRESS_HANDLING(self):
        return os.getenv('URO_DISABLE_INGRESS_HANDLING', 'False').lower() in ['true', '1']

    @property
    def EXCLUDED_DOMAINS(self):
        return tuple(os.getenv('URO_EXCLUDED_DOMAINS', 'default.local').split(","))

    def get_DEFAULT_HEADERS(self, logger):
        headers = os.getenv('URO_DEFAULT_HEADERS', '{}')
        logger.info(f"Retrieved headers string: {headers}")
        headersObj = json.loads(headers)
        logger.info(f"Deserialized to obj: {headersObj}")
        return headersObj

    @property
    def DEFAULT_MONITOR_TYPE(self):
        return os.getenv('URO_DEFAULT_MONITOR_TYPE', 'HTTPS')
    
    @property
    def UPTIMEROBOT_API_KEY(self):
        return os.environ['UPTIMEROBOT_API_KEY']
