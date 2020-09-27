from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class Person(BaseModel):
    uid: Optional[str]
    sub: Optional[str]
    name: Optional[str]
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
        super().__init__(**kwargs)

    async def normalize(self):
        if self.email:
            self.username = self.email.split('@')[0]


Person.update_forward_refs()


class ChildrenModel(BaseModel):
    children: List[Person]
