from pydantic import BaseModel

class GameRawg(BaseModel):
    game_id: int
    name: str
    picture: str | None = None
    year: int


class Game(GameRawg):
    like_count: int
    gamerboxd_rating: float


class GamesOut(BaseModel):
    count: int
    games: list[Game]