from models.schemas import *
from services.db_services import DB_create_game, DB_read_game_likes, DB_read_game_avg_rating
from utils.db import DB_Result

async def search_rawg_games(conn, exconn, url, page_size):
    async with exconn.get(url) as response:
        json = await response.json()
    
    games_list = []
    for i in range(page_size):
        result = json["results"][i]

        game = GameRawg(
            game_id = result["id"],
            name = result["name"],
            picture = result["background_image"],
            year = int(result["released"][0:4])
        )

        games_result = await DB_create_game(conn, game)
        if not games_result.success:
            raise games_result.error
        
        like_count_result = await DB_read_game_likes(conn, game.game_id)

        if not like_count_result.success:
            raise like_count_result.error
    
        avg_review_result = await DB_read_game_avg_rating(conn, game.game_id)

        if not avg_review_result.success:
            raise like_count_result.error
        
        full_game = Game(**game.model_dump(),
                        like_count=like_count_result.obj,
                        gamerboxd_rating=avg_review_result.obj
                    )
        
        games_list.append(full_game)

    games = GamesOut(
        count = page_size,
        games = games_list
    )

    return games