from pydantic import BaseModel

class Review(BaseModel):
    rating_num: float
    rating_text: str | None = None
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