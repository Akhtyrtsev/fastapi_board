# build a schema using pydantic
from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    username: str
    email: str
    id: int


class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    exp: int
    sub: str

