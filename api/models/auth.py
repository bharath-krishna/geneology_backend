from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.openapi.models import OAuthFlows
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakAuthenticationError
from pydantic import ValidationError
from starlette.requests import Request
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from configs.logging import logger
from configs.readers import ConfigReader, SecretReader
from models.users import UserInfo

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
                    status_code=HTTP_401_UNAUTHORIZED,
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


async def require_user(token: str = Depends(oauth2_scheme)) -> UserInfo:
    try:
        userinfo = kc.userinfo(token=token)
    except KeycloakAuthenticationError as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # del userinfo["sub"]
        user = UserInfo(**userinfo)
    except ValidationError as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid resonse",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
