from fastapi import Depends, APIRouter
from typing import Literal
from fastapi.responses import JSONResponse

from services.rawg_services import *
from utils import *

game_router = APIRouter(prefix="/games", tags=["game"])

  
@game_router.get("")
async def search_games(search: str, detail: bool, page: int = 1, page_size: int = 20,
    conn = Depends(get_conn), exconn = Depends(get_exconn), rawg = Depends(get_rawg)):
    """Busca jogos pelo nome"""

    url = rawg + f"&search={search}" + f"&page={page}" + f"&page_size={page_size}"

    games = (await search_rawg_games_complete(conn, exconn, url)
            if detail else await search_rawg_games_overview(conn, exconn, url)) 

    return JSONResponse(games.model_dump())




        