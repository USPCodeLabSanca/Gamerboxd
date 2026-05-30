from models.schemas import *
from services.db_services import DB_create_game
from utils.db import DB_Result

async def search_rawg_games(conn, exconn, url, page_size):
    async with exconn.get(url) as response:
        json = await response.json()
    
    
    games_list = []
    for i in range(page_size):
        result = json["results"][i]
        game = Game(
            game_id = result["id"],
            name = result["name"],
            picture = result["background_image"],
            year = int(result["released"][0:4])
        )
        await DB_create_game(conn, game)
        games_list.append(game)

    games = GamesOut(
        count = page_size,
        games = games_list
    )

    return games