import json
from typing import Optional

from api.configs import AUTH_URL, CLIENT_ID, CLIENT_SECRET, REALM
from api.configs.logging import logger
from fastapi import Depends, HTTPException, status
from fastapi.openapi.models import OAuthFlows
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakAuthenticationError
# from pydantic import ValidationError
from starlette.requests import Request


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


oauth2_scheme = OAuth2Handler(authorizationUrl=F'{AUTH_URL}realms/{REALM}/protocol/openid-connect/auth')


class User():
    def __init__(self, access_token='', refresh_token=''):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.kc = self.keycloak_client()

    def keycloak_client(self):
        return KeycloakOpenID(
            server_url=AUTH_URL,
            client_id=CLIENT_ID,
            client_secret_key=CLIENT_SECRET,
            realm_name=REALM,
            verify=False,
        )

    def get_token(self, username='', password=''):
        return self.kc.token(username=username, password=password)

    async def get_userinfo(self):
        try:
            user = User(access_token=self.access_token)
            self.userinfo = user.kc.userinfo(token=self.access_token)
        except KeycloakAuthenticationError as e:
            error = json.loads(e.error_message)
            logger.error(error['error_description'])
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error['error_description'],
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception:
            raise Exception("TODO")


async def require_user(token: str = Depends(oauth2_scheme)):
    user = User(access_token=token)
    await user.get_userinfo()

    # try:
    #     # del userinfo["sub"]
    #     user = Person(**userinfo)
    #     user.is_authenticated = True
    #     await user.normalize()
    # except ValidationError as e:
    #     logger.error(str(e))
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=json.loads(e.json()),
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    return user
