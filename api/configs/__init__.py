from os import environ

from api.configs.readers import SecretReader

PORT = environ.get('PORT', 8088)
LOG_LEVEL = environ.get('LOG_LEVEL', 'debug')
WORKERS = environ.get('WORKERS', 4)
RELOAD = environ.get('RELOAD', True)
DB_HOST = environ.get('DB_HOST', 'localhost')
DB_PORT = environ.get('DB_PORT', '9080')

AUTH_URL = environ.get('AUTH_URL', 'http://localhost:8099/auth/')
CLIENT_ID = environ.get('CLIENT_ID', 'demo-client')
REALM = environ.get('REALM', 'demo')
CLIENT_SECRET = environ.get('CLIENT_SECRET', SecretReader().get('CLIENT_SECRET'))
