from pydantic import BaseModel

class User(BaseModel):
    """Dados básicos de um usuário"""
    user_id: str
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
    following_count: int


class UserBlocked(BaseModel):
    """Dados sobre os bloqueados pelo usuário"""
    blocked_count: int


class UserOut(User):
    """Dados básicos de saída sobre um usuário"""
    bio: str | None = None
    created_at: str


from .list import ListGames

class UserFeed(UserOut):
    """Dados completos de um usuário"""
    follows: UserFollows
    lists: list[ListGames]