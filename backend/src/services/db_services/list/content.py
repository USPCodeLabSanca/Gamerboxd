from .data import DB_update_list_updated_at
from models.schemas.list import *
from models.schemas.game import GameComplete
from utils import *


@db_query
async def DB_create_list_game(conn, list_id, game_id):
    """Inclui um game em uma lista"""

    await conn.execute('''
        INSERT INTO ListContent(list, game) VALUES($1, $2)
    ''', list_id, game_id)

    await DB_update_list_updated_at(conn, list_id)


@db_query
async def DB_delete_list_game(conn, list_id: str, game_id: int):
    """Remove um game de uma lista"""

    await conn.execute('''
        DELETE FROM ListContent WHERE list = $1 AND game = $2
    ''', list_id, game_id)

    await DB_update_list_updated_at(conn, list_id)


@db_query
async def DB_read_game_in_list(conn, list_id, game_id):
    """Verifica se um game já pertence a uma lista"""

    game_exists = await conn.fetchval('''
        SELECT COUNT(*) FROM ListContent WHERE list = $1 AND game = $2
    ''', list_id, game_id)

    return True if game_exists > 0 else False
    

@db_query
async def DB_read_list_games(conn, list_id: str, page_query: PageQuery):
    """Busca uma página de jogos de uma lista"""

    async with conn.transaction():

        clauses =  PageClauses(
            basic_conditions=[("lc.list = $1", list_id)],
            table_alias="lc",
            col2="game",
            search_col="g.title"
        )

        # Conta quantas jogos da lista correspondem a busca
        where, order_by, cursor_cols, params = build_where(clauses, page_query, True)
        total_games = await conn.fetchval(f'''
            SELECT COUNT(*)
            FROM Games g
            LEFT JOIN ListContent lc ON lc.game = g.id
            WHERE {where}
        ''', *params)

        # Pega uma página de jogo
        where, order_by, cursor_cols, params = build_where(clauses, page_query, False)
        rows = await conn.fetch(f'''
            SELECT g.id AS game_id, g.title, g.picture, g.year,
                COUNT(r.liked) FILTER (WHERE r.liked = true) AS like_count,
                COUNT(r.completed) FILTER (WHERE r.completed = true) AS complete_count,
                COUNT(r.game) AS review_count,
                COALESCE(ROUND(AVG(r.rating_num)::numeric, 2), NULL) AS gamerboxd_rating,
                {cursor_cols}
            FROM Games g
            LEFT JOIN ListContent lc ON lc.game = g.id
            LEFT JOIN Reviews r ON r.game = g.id
            WHERE {where}
            GROUP BY g.id, g.title, g.picture, g.year, lc.created_at, lc.game
            ORDER BY {order_by}
            LIMIT ${len(params)}
        ''', *params)

        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])

        games = [GameComplete(
            game_id=r["game_id"],
            title=r["title"],
            picture=r["picture"],
            year=r["year"],
            like_count=r["like_count"],
            completed_count=r["complete_count"],
            review_count=r["review_count"],
            gamerboxd_rating=float(r["gamerboxd_rating"]) if r["gamerboxd_rating"] is not None else None
        ) for r in rows]

        return PageResult(
            total=total_games,
            page_len=len(rows),
            content=games,
            current_url=page_query.cursor,
            next_url=encode_tuple_to_cursor(rows[-1]["main_col"], rows[-1]["other_col"]) if has_more else None
        )



