from pydantic import BaseModel

class User(BaseModel):
    username: str
    pfp: str | None


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


class ListIn(BaseModel):
    name: str
    description: str = None
    is_private: bool = True    


class List(ListIn):
    creator: str


class GameRawg(BaseModel):
    game_id: int
    name: str
    picture: str | None
    year: int

class Game(GameRawg):
    like_count: int
    gamerboxd_rating: float


class ListOut(List):
    created_at: str
    list_saves: int


class ListFull(ListOut):
    games: list[Game]


class UserLists(BaseModel):
    list_count: int
    lists: list[ListOut]


class UserOut(User):
    email: str
    bio: str | None
    created_at: str


class UserFull(UserOut):
    follows: UserFollows
    lists: UserLists


class GamesOut(BaseModel):
    count: int
    games: list[Game]


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