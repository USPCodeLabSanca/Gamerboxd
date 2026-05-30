from fastapi import Depends, status
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from models.schemas import *
from services.security_services import *
from services.db_services import *
from services.rawg_services import search_rawg_games
from utils.dependencies import get_conn, require_login, get_rawg, get_exconn

game_router = InferringRouter(prefix="/game", tags=["game"])


@cbv(game_router)
class SearchGamesController:
    @game_router.get("/{search}")
    async def search_games(self, search: str, page: int = 1, page_size: int = 20, conn = Depends(get_conn), exconn = Depends(get_exconn), rawg = Depends(get_rawg)):
        
        try:
            url = rawg + f"&search={search}" + f"&page={page}" + f"&page_size={page_size}"
            games = await search_rawg_games(conn, exconn, url, page_size)          

        except Exception as e:
            raise HTTPException(500, detail=str(e))

        return JSONResponse(games.model_dump(), status.HTTP_200_OK)
        #return JSONResponse(json, status.HTTP_200_OK)
        