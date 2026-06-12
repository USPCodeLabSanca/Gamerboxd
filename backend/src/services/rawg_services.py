from models.schemas import *
from services.db_services import DB_create_game
from utils.db import DB_Result

async def search_rawg_games(conn, exconn, url, page_size):
    async with exconn.get(url) as response:
        json = await response.json()
    
    
    games_list = []
    for i in range(page_size):
        result = json["results"][i]

        game = Game_Rawg(
            game_id = result["id"],
            name = result["name"],
            picture = result["background_image"],
            year = int(result["released"][0:4])
        )

        games_result = await DB_create_game(conn, game)
        if not games_result.success:
            raise games_result.error
        
        game_id = games_result.obj
        
        games_list.append(game)

    games = GamesOut(
        count = page_size,
        games = games_list
    )

    return games