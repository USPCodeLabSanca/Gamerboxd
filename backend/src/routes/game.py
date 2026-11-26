from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from ..services.rawg_services import *
from ..services.db_services.game import DB_read_game_full, DB_read_game_page_full, DB_read_game_page_overview
from . import dependencies as dep
from ..utils import errors as err

game_router = APIRouter(prefix="/games", tags=["game"])

  
@game_router.get("")
async def search_games(detail: bool, search: str = "", page: int = 1, page_size: int = 20,
        conn = Depends(dep.get_conn), exconn = Depends(dep.get_exconn), rawg = Depends(dep.get_rawg)):
        """Busca jogos pelo nome"""

        #url = rawg + f"&search={search}" + f"&page={page}" + f"&page_size={page_size}"
        #games = (await search_rawg_games_complete(conn, exconn, url)
        #        if detail else await search_rawg_games_overview(conn, exconn, url)) 

        games = (await DB_read_game_page_full(conn, search, page_size, page)
                if detail else await DB_read_game_page_overview(conn, search, page_size, page))
        
        return JSONResponse(games.model_dump())


@game_router.get("/{game_id}")
async def search_game(game_id: int, conn = Depends(dep.get_conn)):
    """Busca dados completos de um jogo pelo game_id"""

    game = await DB_read_game_full(conn, game_id)

    if game is None:
        raise err.QueryError(404, err.GAME_NOT_FOUND_MSG)

    return JSONResponse(game.model_dump())



        