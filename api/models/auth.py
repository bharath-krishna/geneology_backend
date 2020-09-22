from typing import Optional

from fastapi import HTTPException, status
from fastapi.openapi.models import OAuthFlows
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from keycloak import KeycloakOpenID
from starlette.requests import Request

from api.configs.logging import logger
from api.configs.readers import ConfigReader, SecretReader

kc = KeycloakOpenID(
    server_url=ConfigReader().get('AUTH_URL'),
    client_id=ConfigReader().get('CLIENT_ID'),
    client_secret_key=SecretReader().get('CLIENT_SECRET'),
    realm_name=ConfigReader().get('REALM'),
    verify=False,
)


class OAuth2Handler(OAuth2):
    authorizationUrl: str

    def __init__(self, authorizationUrl):
        flows = OAuthFlows(implicit={"authorizationUrl": authorizationUrl})
        super().__init__(flows=flows)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, token = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                logger.error(self.auto_error)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        store_in_cookie(fastapi_token=token)
        return token


def store_in_cookie(**kwargs):
    for k, v in kwargs.items():
        pass


oauth2_scheme = OAuth2Handler(authorizationUrl='http://localhost:8099/auth/realms/demo/protocol/openid-connect/auth')
