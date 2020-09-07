import logging


class BaseLoggingConfig():
    version = 1
    # level = logging.DEBUG
    formatters = {
        'default': {
            'format': '%(asctime)s %(levelname)+8.8s [%(name)s] - %(message)s ',
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

    # Level      Value
    # CRITICAL    50
    # ERROR       40
    # WARNING     30
    # INFO        20
    # DEBUG       10
    # NOTSET      0

    loggers = {
        "uvicorn.access": {
            "level": "DEBUG",
            "handlers": ['uvicorn_access_console'],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "DEBUG",
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


log_config = BaseLoggingConfig()
logger = log_config.get_logger('api')
