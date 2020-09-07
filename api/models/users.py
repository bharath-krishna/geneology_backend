from pydantic import BaseModel


class UserInfo(BaseModel):
    sub: str
    email_verified: bool
    preferred_username: str
    username: str
