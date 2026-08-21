from pydantic import BaseModel
from .list import UserLists

class User(BaseModel):
    """Dados básicos de um usuário"""
    username: str
    pfp: str | None = None


class UserAuth(BaseModel):
    """Dados necessários para fazer o login"""
    email_or_username: str
    password: str


class UserIn(BaseModel):
    """Dados básicos para criar uma conta"""
    username: str
    email: str
    password: str


class UserEdit(User):
    """Dados básicos para editar uma conta"""
    email: str
    bio: str | None = None


class UserFollows(BaseModel):
    """Dados sobre os seguidores e os seguidos do usuário"""
    follower_count: int
    followers: list[User]
    following_count: int
    followings: list[User]


class UserBlocked(BaseModel):
    """Dados sobre os bloqueados pelo usuário"""
    blocked_count: int
    blocks: list[User]


class UserOut(User):
    """Dados básicos de saída sobre um usuário"""
    email: str
    bio: str | None = None
    created_at: str


class UserFull(UserOut):
    """Dados completos de um usuário"""
    follows: UserFollows
    lists: UserLists