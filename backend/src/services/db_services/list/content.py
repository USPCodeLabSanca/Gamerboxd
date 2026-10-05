from .data import DB_update_list_updated_at
from models.schemas.list import *
from models.schemas.game import Game
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
async def DB_read_list_games(conn, list_id: str, page_query: PageQuery):
    """Busca uma página de jogos de uma lista"""

    async with conn.transaction():

        basic_condition = ("lc.list = $1", list_id)
        page_query_clauses =  PageQuery(
            cursor="(lc.created_at, lc.game)",
            search="g.name"
        )

        # Conta quantas jogos da lista correspondem a busca
        where, params = build_where(basic_condition, page_query_clauses, page_query, None, True)
        total_games = await conn.fetchval(f'''
            SELECT COUNT(*)
            FROM Games g
            LEFT JOIN ListContent lc ON lc.game = g.id
            WHERE {where}
        ''', *params)

        # Pega uma página de jogo
        where, params = build_where(basic_condition, page_query_clauses, page_query, ">")
        rows = await conn.fetch(f'''
            SELECT g.id AS game_id, g.name, g.picture, g.year, lc.created_at,
                COUNT(r.liked) FILTER (WHERE r.liked = true) AS like_count,
                COUNT(r.completed) FILTER (WHERE r.completed = true) AS complete_count,
                COUNT(r.game) AS review_count,
                COALESCE(ROUND(AVG(r.rating_num)::numeric, 2), -1) AS gamerboxd_rating
            FROM Games g
            LEFT JOIN ListContent lc ON lc.game = g.id
            LEFT JOIN Reviews r ON r.game = g.id
            WHERE {where}
            GROUP BY g.id, g.name, g.picture, g.year, lc.created_at, lc.game
            ORDER BY lc.created_at ASC, lc.game ASC
            LIMIT ${len(params)}
        ''', *params)

        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])

        games = [Game(
            game_id = r["game_id"],
            name = r["name"],
            picture = r["picture"],
            year = r["year"],
            like_count = r["like_count"],
            completed_count = r["complete_count"],
            review_count = r["review_count"],
            gamerboxd_rating = r["gamerboxd_rating"] if r["gamerboxd_rating"] >= 0 else None
        ) for r in rows]

        page_result = PageResult(
            total=total_games,
            page_size=len(rows),
            content=games
        )

        # Monta o cursor para a próxima página de jogos
        page_result.next_page = encode_tuple_to_cursor(rows[-1]["created_at"], rows[-1]["game_id"]) if has_more else None

        # Se o cursor é None, estamos na busca pela primeira página, então com certeza não existe página anterior
        if page_query.cursor is None:
            return page_result

        # Acha o cursor para a página de jogos anterior
        where, params = build_where(basic_condition, page_query_clauses, page_query, "<=")
        print("here3")
        rows = await conn.fetch(f'''
            SELECT lc.game, lc.created_at
            From Games g
            LEFT JOIN ListContent lc ON lc.game = g.id
            WHERE {where}
            ORDER BY lc.created_at DESC, lc.game DESC
            LIMIT ${len(params)}
        ''', *params)

        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])

        page_result.current_page = page_query.cursor
        page_result.previous_page = encode_tuple_to_cursor(rows[-1]["created_at"], rows[-1]["game"]) if has_more else None

        return page_result


