from pydantic import BaseModel

from .game import GameOverview
from .user import User


class List(BaseModel):
    """Dados básicos de uma lista"""
    name: str                               # Nome da lista
    description: str | None = None          # Descrição da lista
    privacy: int                            # Privacidade da lista


class ListNew(List):
    """Dados das listas ao criar"""
    first_games: list[int]


class ListEdit(List):
    """Dados das listas ao editar"""
    list_id: str


class ListOutOverview(BaseModel):
    """Dados das listas resumidos"""
    name: str                               # Nome da lista
    list_id: str                            # Id da lista no DB
    creator: User                           # Dados do criador da lista (id, username, pfp)
    saves_count: int                        # Quantos pessoas salvaram a lista
    cover_picture: str | None               # URL de uma imagem de game que pertence à lista
    rel: int | None = None                  # Relacionamento de quem está vendo a lista com a lista


class ListOutComplete(List):
    """Dados das listas completos"""
    list_id: str                            # Id da lista no DB
    creator: User                           # Dados do criador da lista (id, username, pfp)
    saves_count: int                        # Quantos pessoas salvaram a lista
    games_count: int                        # Quantos games tem na lista
    cover_picture: str | None               # URL de uma imagem de game que pertence à lista
    rel: int | None = None                  # Relacionamento de quem está vendo a lista com a lista
    created_at: str                         # Data de criação da lista
    updated_at: str


class ListGames(BaseModel):
    """Dados básicos dos primeiros games que pertencem a uma lista"""
    list_id: str                    # Id da lista no DB
    name: str                       # Nome da lista
    games: list[GameOverview]       # Lista com até 4 jogos que pertencem à lista
