from models.schemas.game import *
from services.db_services.game import *


async def search_rawg_games(conn, exconn, url, page_size):
    """Busca games na API Rawg"""

    async with exconn.get(url) as response:
        json = await response.json()

    games_list = []
    for i in range(page_size):

        result = json["results"][i]

        game = GameRawg(
            game_id = result["id"],
            name = result["name"],
            picture = result["background_image"],
            year = int(result["released"][0:4]) if result["released"] is not None else None
        )

        async with conn.transaction():
            game_is_already_in_DB = await DB_create_game(conn, game)

        if not game_is_already_in_DB:
            like_count = await DB_read_game_count_likes(conn, game.game_id)
            review_count = await DB_read_game_count_reviews(conn, game.game_id)
            completed_count = await DB_read_game_count_completed(conn, game.game_id)
            avg_review = await DB_read_game_avg_rating(conn, game.game_id)

        else:
            like_count = 0
            review_count = 0
            completed_count = 0
            avg_review = None


        full_game = Game(
            **game.model_dump(),
            like_count=like_count,
            review_count=review_count,
            completed_count=completed_count,
            gamerboxd_rating=avg_review
        )
        
        games_list.append(full_game)

    games = GamesOut(
        count = page_size,
        games = games_list
    )

    return games