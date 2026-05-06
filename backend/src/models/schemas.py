from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    password: str
    pfp: int = None
    bio: str = None
    tags: list[int] = []


class List(BaseModel):
    creator: str = None
    name: str
    description: str
    is_private: bool = True


class Auth_login(BaseModel):
    email_or_username: str
    password: str