from models.schemas.game import *
from utils.utils import db_query


@db_query
async def DB_create_game(conn, game: GameOverview):
    """Adiciona um jogo ao BD"""

    already_exists = await conn.fetchrow('''
        INSERT INTO Games(id, title, picture, year)
        VALUES($1, $2, $3, $4)
        ON CONFLICT (id)
        DO UPDATE SET title = $2, picture = $3, year = $4
        RETURNING id
    ''', game.game_id, game.title, game.picture, game.year)

    return False if already_exists is None else True


@db_query    
async def DB_read_game_name(conn, game_id: int):
    """Lê o nome de um game do DB a partir do seu id"""

    game_name = await conn.fetchval('''
        SELECT name
        FROM Games
        WHERE id = $1
    ''', game_id)

    return game_name


@db_query
async def DB_read_game_full(conn, game_id: int):
    """Lê os dados completos sobre um game no DB usando o id dele"""

    game = await conn.fetchrow('''
        SELECT g.*,
            COUNT(r.id) FILTER (WHERE r.liked = true)     AS like_count,
            COUNT(r.id) FILTER (WHERE r.completed = true) AS completed_count,
            COUNT(r.id)                                   AS review_count,
            COALESCE(ROUND(AVG(r.rating_num)::numeric, 2), NULL) AS avg_rating
        FROM Games g
        LEFT JOIN Reviews r ON r.game = g.id
        WHERE g.id = $1
        GROUP BY g.id
    ''', game_id)

    if game is None:
        return None

    return GameComplete(
        game_id=game["id"],
        title=game["title"],
        picture=game["picture"],
        year=game["year"],
        like_count=game["like_count"],
        completed_count=game["completed_count"],
        review_count=game["review_count"],
        gamerboxd_rating=float(game["avg_rating"]) if game["avg_rating"] is not None else None
    )


@db_query
async def DB_read_game_basic(conn, game_id: int):
    """Lê dados básicos sobre um game no DB usando o id dele"""

    game = await conn.fetchrow('''
        SELECT g.* FROM Games g WHERE g.id = $1
    ''', game_id)

    if game is None:
        return None

    return GameOverview(
        game_id=game["id"],
        title=game["title"],
        picture=game["picture"],
        year=game["year"]
    )

