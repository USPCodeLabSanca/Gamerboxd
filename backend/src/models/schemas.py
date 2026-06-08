from pydantic import BaseModel

class User(BaseModel):
    username: str
    pfp: str = None


class UserAuth(BaseModel):
    email_or_username: str
    password: str


class UserTags(BaseModel):
    tag_count: int
    tags: list[str] = []


class UserIn(User):
    email: str
    password: str
    bio: str = None
    tags: UserTags


class UserFollows(BaseModel):
    follower_count: int
    followers: list[User]
    following_count: int
    followings: list[User]


class UserBlocked(BaseModel):
    blocked_count: int
    blocks: list[User]


class ListIn(BaseModel):
    name: str
    description: str
    is_private: bool = True    


class List(ListIn):
    creator: str


class ListFull(List):
    created_at: str
    list_saves: int


class UserLists(BaseModel):
    list_count: int
    lists: list[ListFull]


class UserOut(User):
    email: str
    bio: str = None
    created_at: str


class UserFull(UserOut):
    tags: UserTags
    follows: UserFollows
    lists: UserLists

  
class Game(BaseModel):
    game_id: int
    name: str
    image: str


class ListOut(List):
    games: list[Game]
    created_at: str
    last_update: str


class Review(BaseModel):
    rating_num: float
    rating_text: str
    liked: bool


class ReviewIn(Review):
    game: int
    is_private: bool
    time_played: float
    completed: bool


class ReviewOut(Review):
    likes_count: int
    game_name: str
    created_at: str


class ReviewOutOne(ReviewOut):
    username: str
    tag_count: int
    tags: list[str] = []
    completed: bool
    time_played: float
    last_update: str

class ReviewAll(ReviewOutOne):
    review_id: str

class ReviewLike(BaseModel):
    user_a: str
    review: str