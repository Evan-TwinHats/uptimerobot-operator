"""Config properties from environment variables"""
import os


class Config:
    """Config properties from environment variables"""
    @property
    def DISABLE_INGRESS_HANDLING(self):
        """Flag for disabling ingress handling"""
        return os.getenv('URO_DISABLE_INGRESS_HANDLING', 'False').lower() in ['true', '1']

    @property
    def EXCLUDED_DOMAINS(self):
        """Domains excluded from processing in ingresses"""
        return tuple(os.getenv('URO_EXCLUDED_DOMAINS', 'default.local').split(","))

    @property
    def DEFAULT_HEADERS(self):
        """Default headers to include in every monitor"""
        return os.getenv('URO_DEFAULT_HEADERS', '{}')

    @property
    def DEFAULT_MONITOR_TYPE(self):
        """Default type for monitors where one was not specified"""
        return os.getenv('URO_DEFAULT_MONITOR_TYPE', 'HTTPS')

    @property
    def UPTIMEROBOT_API_KEY(self):
        """UptimeRobot API key"""
        return os.environ['UPTIMEROBOT_API_KEY']
