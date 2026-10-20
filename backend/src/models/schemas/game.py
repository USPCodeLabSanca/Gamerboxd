from pydantic import BaseModel

class GameOverview(BaseModel):
    """Dados dos games que vem da API RAWG"""
    game_id: int
    title: str
    picture: str | None = None
    year: int | None


class GameComplete(GameOverview):
    """Dados completos dos games"""
    like_count: int
    completed_count: int
    review_count: int
    gamerboxd_rating: float | None


class GamesOut(BaseModel):
    """Lista de games"""
    count: int
    games: list[GameComplete | GameOverview]