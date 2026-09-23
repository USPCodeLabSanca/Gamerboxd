from pydantic import BaseModel

from .game import Game, GameRawg


class ListIn(BaseModel):
    """Dados das listas ao criar/editar"""
    name: str
    description: str | None = None
    is_private: bool = True    


class List(ListIn):
    """Dados das listas ao criar/editar + o criador da lista (user_id)"""
    creator: str


class ListOut(List):
    """Dados das listas completos"""
    created_at: str
    list_saves: int


class ListFull(ListOut):
    """Dados das listas completos + os jogos que pertencem a lista"""
    games: list[Game]


class ListGames(BaseModel):
    """Dados dos primeiros games que pertencem a uma lista"""
    name: str
    count: int
    games: list[GameRawg]


class UserLists(BaseModel):
    """Listas salvas por um usuário"""
    count: int
    lists: list[ListOut]