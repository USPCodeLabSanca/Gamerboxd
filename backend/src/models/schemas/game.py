from pydantic import BaseModel

class GameRawg(BaseModel):
    """Dados dos games que vem da API RAWG"""
    game_id: int
    name: str
    picture: str | None = None
    year: int


class Game(GameRawg):
    """Dados completos dos games"""
    like_count: int
    gamerboxd_rating: float | None


class GamesOut(BaseModel):
    """Lista de games"""
    count: int
    games: list[Game]