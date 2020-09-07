from os import environ

PORT = environ.get('PORT', 8088)
LOG_LEVEL = environ.get('LOG_LEVEL', 'debug')
WORKERS = environ.get('WORKERS', 4)
RELOAD = environ.get('RELOAD', True)
