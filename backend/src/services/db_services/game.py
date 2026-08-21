from models.schemas.game import *
from utils.utils import db_query


@db_query
async def DB_create_game(conn, game: Game):
    await conn.execute('''
        INSERT INTO Games(id, name, picture, year)
        VALUES($1, $2, $3, $4)
        ON CONFLICT
        DO NOTHING;
    ''', game.game_id, game.name, game.picture, game.year)


@db_query    
async def DB_read_game_name(conn, game: int):
    game_name = await conn.fetchval('''
        SELECT name
        FROM Games
        WHERE id = $1
    ''', game)

    return game_name


@db_query
async def DB_read_game_likes(conn, game_id: int):
    like_count = await conn.fetchval('''
        SELECT COUNT(r.liked)
        FROM Reviews r 
        WHERE liked = true
        AND game = $1
    ''', game_id)

    return like_count


@db_query
async def DB_read_game_avg_rating(conn, game_id: int):
    avg_rating = await conn.fetchval('''
        SELECT COALESCE(ROUND(AVG(r.rating_num)::numeric, 2), -1)
        FROM Games g
        JOIN Reviews r ON r.game = g.id
        WHERE g.id = $1
        AND r.is_private = false
    ''', game_id)

    return avg_rating if avg_rating >= 0 else None
