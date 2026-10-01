from pydantic import BaseModel

from .game import GameRawg
from .user import User


class ListIn(BaseModel):
    """Dados das listas ao criar/editar"""
    name: str                               # Nome da lista
    description: str | None = None          # Descrição da lista
    is_private: bool = True                 # Privacidade da lista


class ListOutOverview(BaseModel):
    """Dados das listas resumidos"""
    name: str                               # Nome da lista
    list_id: str                            # Id da lista no DB
    creator: User                           # Dados do criador da lista (id, username, pfp)
    list_saves_count: int                   # Quantos pessoas salvaram a lista


class ListOutComplete(ListIn):
    """Dados das listas completos"""
    list_id: str                            # Id da lista no DB
    created_at: str                         # Data de criação da lista
    creator: User                           # Dados do criador da lista (id, username, pfp)
    list_saves_count: int                   # Quantos pessoas salvaram a lista
    list_games_count: int                   # Quantos games tem na lista


class ListGames(BaseModel):
    """Dados básicos dos primeiros games que pertencem a uma lista"""
    list_id: str                        # Id da lista no DB
    name: str                           # Nome da lista
    games_count: int                    # Quantos jogos que pertencem à lista vão ser enviados (<4)
    games: list[GameRawg | None]        # Lista com até 4 jogos que pertencem à lista
