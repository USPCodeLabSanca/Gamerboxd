from models.schemas.game import *
from services.db_services import DB_create_game, DB_read_game_likes, DB_read_game_avg_rating


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

        async with conn.transaction():
            await DB_create_game(conn, game)

        like_count = await DB_read_game_likes(conn, game.game_id)
        avg_review = await DB_read_game_avg_rating(conn, game.game_id)

        full_game = Game(**game.model_dump(),
                        like_count=like_count,
                        gamerboxd_rating=avg_review)
        
        games_list.append(full_game)

    games = GamesOut(
        count = page_size,
        games = games_list
    )

    return games