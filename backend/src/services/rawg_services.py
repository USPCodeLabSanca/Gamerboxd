from models.schemas.game import *
from services.db_services.game import *
from aiohttp.client_exceptions import ContentTypeError

from utils.errors import *


async def search_rawg_games_complete(conn, exconn, url):
    """Busca games na API Rawg e retorna infos completas sobre eles"""

    async with exconn.get(url) as response:
        try:
            json = await response.json()

        except ContentTypeError:
            text = await response.text()
            raise QueryError(502, f"API RAWG falhou. Retorno: {text}")

    games_list = []
    for i in range(len(json["results"])):

        result = json["results"][i]

        game = GameOverview(
            game_id = result["id"],
            title = result["name"],
            picture = result["background_image"],
            year = int(result["released"][0:4]) if result["released"] is not None else None
        )

        async with conn.transaction():
            game_is_already_in_DB = await DB_create_game(conn, game)

        if game_is_already_in_DB:
            full_game = await DB_read_game_full(conn, result["id"])

        else:
            full_game = GameComplete(
                **game.model_dump(),
                like_count=0,
                review_count=0,
                completed_count=0,
                gamerboxd_rating=0
            )
        
        games_list.append(full_game)

    games = GamesOut(
        total = json["count"],
        count = len(json["results"]),
        games = games_list
    )

    return games


async def search_rawg_games_overview(conn, exconn, url):
    """Busca games na API Rawg e retorna infos básicas sobre eles"""
    
    async with exconn.get(url) as response:
        json = await response.json()

    games_list = []
    for i in range(len(json["results"])):

        result = json["results"][i]

        game = GameOverview(
            game_id = result["id"],
            title = result["name"],
            picture = result["background_image"],
            year = int(result["released"][:4]) if result["released"] is not None else None
        )

        async with conn.transaction():
            await DB_create_game(conn, game)
        
        games_list.append(game)

    games = GamesOut(
        total = json["count"],
        count = len(json["results"]),
        games = games_list
    )

    return games