from models.schemas.game import *
from utils.utils import db_query


@db_query
async def DB_create_game(conn, game: Game):
    """Adiciona um jogo ao BD"""

    already_exists = await conn.fetchrow('''
        INSERT INTO Games(id, name, picture, year)
        VALUES($1, $2, $3, $4)
        ON CONFLICT (id)
        DO UPDATE SET name = $2, picture = $3, year = $4
        RETURNING id
    ''', game.game_id, game.name, game.picture, game.year)

    return False if already_exists is None else True


@db_query    
async def DB_read_game_name(conn, game: int):
    """Lê o nome de um game do BD a partir do seu id"""

    game_name = await conn.fetchval('''
        SELECT name
        FROM Games
        WHERE id = $1
    ''', game)

    return game_name


@db_query
async def DB_read_game_count_likes(conn, game_id: int):
    """Conta quantas reviews disseram que gostaram do jogo"""

    like_count = await conn.fetchval('''
        SELECT COUNT(r.liked)
        FROM Reviews r 
        WHERE r.liked = true AND r.game = $1
    ''', game_id)

    return like_count


@db_query
async def DB_read_game_avg_rating(conn, game_id: int):
    """Acha a média das avaliações do jogo"""

    avg_rating = await conn.fetchval('''
        SELECT COALESCE(ROUND(AVG(r.rating_num)::numeric, 2), -1)
        FROM Games g
        JOIN Reviews r ON r.game = g.id
        WHERE g.id = $1
    ''', game_id)

    return avg_rating if avg_rating >= 0 else None


@db_query
async def DB_read_game_count_completed(conn, game_id: int):
    """Conta quantos usuários marcaram o game como completado"""

    return await conn.fetchval('''
        SELECT COUNT(r.completed)
        FROM Reviews r 
        WHERE r.completed = true AND r.game = $1
    ''', game_id)


@db_query
async def DB_read_game_count_reviews(conn, game_id: int):
    """Conta quantas reviews o game tem"""

    return await conn.fetchval('''
        SELECT COUNT(*r.game
        FROM Reviews r 
        WHERE r.game = $1
    ''', game_id)

