import base64
import json
from os import environ

_secrets = {}


class ConfigReader():
    def __init__(self, env_name='FASTAPI_CONFIGS'):
        secrets = environ.get(env_name)
        if not secrets:
            raise Exception(f'"{env_name}" environment varible not set')
        global _secrets

        if not _secrets:
            # if secret file not exist, raise exception and quit.
            _secrets = json.loads(base64.b64decode(bytes(secrets, 'utf-8')))

    def get(self, secret_key):
        global _secrets
        return _secrets.get(secret_key, None)


class SecretReader(ConfigReader):
    def __init__(self):
        super().__init__(env_name='FASTAPI_SECRETS')
