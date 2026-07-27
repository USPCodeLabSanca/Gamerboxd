from pydantic import BaseModel
from .list import UserLists

class User(BaseModel):
    username: str
    pfp: str | None = None


class UserAuth(BaseModel):
    email_or_username: str
    password: str


class UserIn(BaseModel):
    username: str
    email: str
    password: str


class UserEdit(User):
    email: str
    bio: str


class UserFollows(BaseModel):
    follower_count: int
    followers: list[User]
    following_count: int
    followings: list[User]


class UserBlocked(BaseModel):
    blocked_count: int
    blocks: list[User]


class UserOut(User):
    email: str
    bio: str | None = None
    created_at: str


class UserFull(UserOut):
    follows: UserFollows
    lists: UserLists