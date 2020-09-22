from __future__ import annotations

import json
from typing import List, Optional

from fastapi import Depends, HTTPException
from keycloak.exceptions import KeycloakAuthenticationError
from pydantic import BaseModel, ValidationError
from starlette import status

from api.configs.logging import logger
from api.models.auth import kc, oauth2_scheme


class Person(BaseModel):
    uid: Optional[str]
    sub: Optional[str]
    name: str
    email: Optional[str]
    kcid: Optional[str]
    gender: Optional[str]
    created_by: Optional[str]
    username: Optional[str]
    partners: List[Person] = []
    parents: List[Person] = []
    children: List[Person] = []
    is_authenticated: bool = False

    def __init__(self, **kwargs):
        kwargs['dgraph.type'] = "Person"
        # TODO: move below code to somewhere else and make created_by: str
        # kwargs['created_by'] = kwargs['email']
        super().__init__(**kwargs)

    @classmethod
    async def require_user(cls, token: str = Depends(oauth2_scheme)):
        try:
            userinfo = kc.userinfo(token=token)
        except KeycloakAuthenticationError as e:
            error = json.loads(e.error_message)
            logger.error(error['error_description'])
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error['error_description'],
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            # del userinfo["sub"]
            user = cls(**userinfo)
            user.is_authenticated = True
            await user.normalize()
        except ValidationError as e:
            logger.error(str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=json.loads(e.json()),
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    async def normalize(self):
        self.username = self.email.split('@')[0]


Person.update_forward_refs()
