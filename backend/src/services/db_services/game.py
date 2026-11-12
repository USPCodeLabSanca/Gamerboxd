from ...models.schemas.game import GameOverview, GameComplete, GamesOut
from ...utils.utils import db_query, escape_like

@db_query
async def DB_create_game(conn, game: GameOverview, relevancy: int):
    """Adiciona um jogo ao DB"""

    already_exists = await conn.fetchrow('''
        INSERT INTO Games(id, title, picture, year, relevancy)
        VALUES($1, $2, $3, $4, $5)
        ON CONFLICT (id)
        DO UPDATE SET title = $2, picture = $3, year = $4
        RETURNING id
    ''', game.game_id, game.title, game.picture, game.year, relevancy)

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
            COUNT(r.id) FILTER (WHERE r.game = g.id)      AS review_count,
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


async def DB_read_game_page_full(conn, search: str, page_size: int, page: int):
    """Lê os dados completos sobre uma página de games a partir de um termo de busca de titulo"""

    search_term = f"%{escape_like(search)}%"

    total = await conn.fetchval('''
        SELECT COUNT(*)
        FROM Games g
        WHERE g.title ILIKE $1
    ''', search_term)

    if total == 0:
        return GamesOut(
            total = 0,
            count = 0,
            games = []
        )

    games = await conn.fetch('''
        SELECT g.id, g.title, g.picture, g.year,
            COUNT(r.id) FILTER (WHERE r.liked = true)     AS like_count,
            COUNT(r.id) FILTER (WHERE r.completed = true) AS completed_count,
            COUNT(r.id) FILTER (WHERE r.game = g.id)      AS review_count,
            COALESCE(ROUND(AVG(r.rating_num)::numeric, 2), NULL) AS avg_rating
        FROM Games g
        LEFT JOIN Reviews r ON r.game = g.id
        WHERE g.title ILIKE $1
        GROUP BY g.id
        ORDER BY 
            g.relevancy DESC,
            g.title ILIKE $2 DESC,
            length(g.title) ASC,
            g.title ASC
        LIMIT $3
        OFFSET $4
    ''', search_term, search_term[:-1], page_size, page_size*(page-1))

    return GamesOut(
        total = total,
        count = len(games),
        games = [
            GameComplete(
                game_id=game["id"],
                title=game["title"],
                picture=game["picture"],
                year=game["year"],
                like_count=game["like_count"],
                completed_count=game["completed_count"],
                review_count=game["review_count"],
                gamerboxd_rating=float(game["avg_rating"]) if game["avg_rating"] is not None else None
        ) for game in games]
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


@db_query
async def DB_read_game_page_overview(conn, search: str, page_size: int, page: int):
    """Lê os dados resumidos sobre uma página de games a partir de um termo de busca de titulo"""

    search_term = f"%{escape_like(search)}%"

    total = await conn.fetchval('''
        SELECT COUNT(*)
        FROM Games g
        WHERE g.title ILIKE $1
    ''', search_term)

    if total == 0:
        return GamesOut(
            total = 0,
            count = 0,
            games = []
        )

    games = await conn.fetch('''
        SELECT g.id, g.title, g.picture, g.year
        FROM Games g
        WHERE g.title ILIKE $1
        GROUP BY g.id
        ORDER BY 
            g.relevancy DESC,
            g.title ILIKE $2 DESC,
            length(g.title) ASC,
            g.title ASC
        LIMIT $3
        OFFSET $4
    ''', search_term, search_term[:-1], page_size, page_size*(page-1))

    return GamesOut(
        total = total,
        count = len(games),
        games = [
            GameOverview(
                game_id=game["id"],
                title=game["title"],
                picture=game["picture"],
                year=game["year"]
            ) for game in games]
    )


@db_query 
async def DB_read_last_game(conn):
    """Lê o maior game_id presente no DB"""

    return await conn.fetchval('''
        SELECT g.id FROM Games g 
        ORDER BY g.id DESC
        LIMIT 1
    ''',)


@db_query 
async def DB_delete_game(conn, game_id: int):
    """Remove um game do DB"""

    return await conn.execute('''
        DELETE FROM Games g 
        WHERE g.id = $1
    ''', game_id)