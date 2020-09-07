from os import environ

PORT = environ.get('PORT', 8080)
LOG_LEVEL = environ.get('LOG_LEVEL', 'debug')
WORKERS = environ.get('WORKERS', 30)
RELOAD = environ.get('RELOAD', True)
