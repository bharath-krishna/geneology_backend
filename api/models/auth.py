import json
from typing import Any, Optional

from api.configurations.base import config
from fastapi import Depends, HTTPException, Request, status
from fastapi.openapi.models import OAuthFlows
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jose.exceptions import (ExpiredSignatureError, JWKError, JWTClaimsError, JWTError)
from keycloak import KeycloakOpenID
from keycloak.exceptions import (KeycloakAuthenticationError, KeycloakConnectionError)


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
                config.logger.error(self.auto_error)
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
            else:
                return None
        store_in_cookie(fastapi_token=token)
        return token


def store_in_cookie(**kwargs):
    for k, v in kwargs.items():
        pass


oauth2_scheme = OAuth2Handler(authorizationUrl=F'{config.auth_url}realms/{config.realm}/protocol/openid-connect/auth')


class User():
    def __init__(self, access_token='', refresh_token=''):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.kc = self.keycloak_client()
        self.userinfo = self.get_userinfo()

    @classmethod
    def keycloak_client(self):
        return KeycloakOpenID(
            server_url=config.auth_url,
            client_id=config.client_id,
            realm_name=config.realm,
            verify=False,
        )

    @property
    def email(self):
        return self.userinfo.get('email', 'N/A')

    @property
    def name(self):
        name = self.userinfo.get('name')
        if not name:
            # use first part of the email
            parts = self.email.split('@')
            if not parts or len(parts) != 2:
                self.name = self.email
            else:
                self.name = parts[0]

    @property
    def username(self):
        return self.userinfo['preferred_username']

    def get_token(self, username='', password=''):
        return self.kc.token(username=username, password=password)

    @classmethod
    def random_test_user(cls):
        token = cls.test_user_token()
        return cls.log_user_in(access_token=token['access_token'], refresh_token=token['refresh_token'])

    @classmethod
    def log_user_in(cls, access_token: str, refresh_token: str = '') -> Any:
        user = cls(access_token, refresh_token)
        if not user or not user.is_authenticated:
            return None
        return user

    @property
    def is_authenticated(self) -> bool:
        return bool(self.token_info(verify_aud=False))

    def token_info(self, verify_signature=True, verify_aud=True, exp=True):
        public_key = self.kc.public_key()
        keycloak_public_key = f'-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----'
        options = {'verify_signature': verify_signature, 'verify_aud': verify_aud, "exp": exp}

        try:
            return self.kc.decode_token(self.access_token,
                                        key=keycloak_public_key,
                                        algorithms=['RS256'],
                                        options=options)
        except (JWKError, JWTClaimsError, JWTError, ExpiredSignatureError) as e:
            config.logger.error(f'{e.__class__.__name__}: {str(e)} {self.access_token}')
        except Exception as e:
            config.logger.error(f'Unknown token exception: {e.__class__.__name__} {str(e)} {self.access_token}')

        return False

    @classmethod
    def test_user_token(cls, username=None, password=None):
        kc = cls.keycloak_client()

        if not username:
            username = 'username'

        if not password:
            password = 'password'
        return kc.token(username=username, password=password, grant_type=['password'])

    def get_userinfo(self):
        try:
            userinfo = self.kc.userinfo(token=self.access_token)
        except KeycloakAuthenticationError as e:
            error = json.loads(e.error_message)
            config.logger.error(error['error_description'])
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error['error_description'],
                headers={"WWW-Authenticate": "Bearer"},
            )
        except KeycloakConnectionError as e:
            error = json.loads(e.error_message)
            config.logger.error(error['error_description'])
            raise HTTPException(
                status_code=status.HTTP_400_UNAUTHORIZED,
                detail=error['error_description'],
                headers={"WWW-Authenticate": "Bearer"},
            )
        return userinfo


async def require_user(request: Request, access_token: str = Depends(oauth2_scheme)):
    user = User.log_user_in(access_token=access_token)
    config.logger.info(f"User {user.username} authenticated")
    request.state.user = user
    return user
