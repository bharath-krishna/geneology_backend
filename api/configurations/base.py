import logging.config
from functools import lru_cache
from os import environ

from api.configurations.readers import SecretReader
from pydantic import AnyHttpUrl, BaseSettings


class BaseLoggingConfig():
    version = 1
    formatters = {
        'default': {
            'format': '%(asctime)s %(levelname)+8.8s [%(name)s] - %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S%z',
        },
        'dict': {
            'format': '{"time": \"%(asctime)s\", "level": \"%(levelname)s\", '
                      '"name": \"[%(name)s]\", "message": \"%(message)s\"}',
            'datefmt': '%Y-%m-%dT%H:%M:%S%z',
        },
    }
    handlers = {
        'console': {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "dict",
        },
        'uvicorn_access_console': {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "dict",
        },
        'uvicorn_access_file': {
            "class": "logging.FileHandler",
            'filename': 'uvicorn_access.log',
            "formatter": "dict",
        },
    }
    root = {'handlers': ['console']}
    loggers = {
        "uvicorn": {
            "level": "DEBUG",
            "handlers": ['console'],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ['console'],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
        "urllib3.connectionpool": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
        "urllib3.util.retry": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
    }

    def __init__(self):
        logging.config.dictConfig(self.to_dict())

    def get_logger(self, name):
        return logging.getLogger(name)

    def to_dict(self):
        return {k: getattr(self, k) for k in dir(self) if not (k.startswith('_') or callable(getattr(self, k)))}

# logging.getLogger("urllib3.connectionpool").setLevel(logging.DEBUG)
# logging.getLogger("urllib3.util.retry").setLevel(logging.DEBUG)

log_config = BaseLoggingConfig()
logger = log_config.get_logger('api')

class Settings(BaseSettings):
    version: str = '0.0.1'
    title: str = "Geneology Project - Backend"
    logger: logging.Logger = logger
    prefix: str = environ.get('API_PREFIX', '/v1')
    host: str = environ.get('API_HOST', '0.0.0.0')
    port: int = environ.get('API_PORT', 8088)
    log_level: str = environ.get('API_LOG_LEVEL', 'debug')
    workers: int = environ.get('API_WORKERS', 4)
    reload: bool = environ.get('API_RELOAD', True)
    db_host: str = environ.get('API_DB_HOST', 'localhost')
    db_port: int = environ.get('API_DB_PORT', 9080)
    auth_url: AnyHttpUrl = environ.get('API_AUTH_URL', 'http://localhost:8099/auth/')
    client_id: str = environ.get('API_CLIENT_ID', 'demo-client')
    realm: str = environ.get('API_REALM', 'demo')
    client_secret: str = environ.get('API_CLIENT_SECRET', 'somesecret')
    access_log: bool = environ.get('API_ACCESS_LOG', True)
    debug: bool = environ.get('API_DEBUG', True)

    class Config:
        env_prefix = 'API_'

@lru_cache()
def get_settings():
    return Settings()

config = get_settings()
