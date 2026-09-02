from pydantic import BaseModel

class Review(BaseModel):
    """Dados básicos de uma review"""
    rating_num: float
    rating_text: str | None = None
    liked: bool


class ReviewIn(Review):
    """Dados de entrada sobre uma review"""
    game: int
    is_private: bool
    time_played: float
    completed: bool


class ReviewOut(Review):
    """Dados de saída sobre uma review"""
    likes_count: int
    game_name: str
    created_at: str


class ReviewOutOne(ReviewOut):
    """Dados de saída completos sobre uma review"""
    username: str
    tag_count: int
    tags: list[str] = []
    completed: bool
    time_played: float
    last_update: str


class ReviewAll(ReviewOutOne):
    """Dados de saída completos sobre uma review + review_id"""
    review_id: str


class ReviewLike(BaseModel):
    """Dados sobre o like de uma review"""
    user: str
    review: str