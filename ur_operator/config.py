import os
import json

class Config:
    @property
    def DISABLE_INGRESS_HANDLING(self):
        return os.getenv('URO_DISABLE_INGRESS_HANDLING', 'False').lower() in ['true', '1']

    @property
    def EXCLUDED_DOMAINS(self):
        return tuple(os.getenv('URO_EXCLUDED_DOMAINS', 'default.local').split(","))

    def DEFAULT_HEADERS(self):
        return json.loads(os.getenv('URO_DEFAULT_HEADERS', {}))

    @property
    def DEFAULT_MONITOR_TYPE(self):
        return os.getenv('URO_DEFAULT_MONITOR_TYPE', 'HTTPS')
    
    @property
    def UPTIMEROBOT_API_KEY(self):
        return os.environ['UPTIMEROBOT_API_KEY']
