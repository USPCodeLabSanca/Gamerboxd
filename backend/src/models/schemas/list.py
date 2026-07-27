from pydantic import BaseModel

from .game import Game


class ListIn(BaseModel):
    name: str
    description: str | None = None
    is_private: bool = True    


class List(ListIn):
    creator: str

class ListOut(List):
    created_at: str
    list_saves: int


class ListFull(ListOut):
    games: list[Game]


class UserLists(BaseModel):
    list_count: int
    lists: list[ListOut]