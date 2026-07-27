from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from services.rawg_services import search_rawg_games
from utils.dependencies import get_conn, get_rawg, get_exconn

game_router = APIRouter(prefix="/game", tags=["game"])

  
@game_router.get("/{search}")
async def search_games(search: str, page: int = 1, page_size: int = 20, conn = Depends(get_conn), exconn = Depends(get_exconn), rawg = Depends(get_rawg)):
    url = rawg + f"&search={search}" + f"&page={page}" + f"&page_size={page_size}"
    games = await search_rawg_games(conn, exconn, url, page_size)          

    return JSONResponse(games.model_dump())
        