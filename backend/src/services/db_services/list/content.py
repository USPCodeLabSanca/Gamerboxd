from .data import DB_update_list_updated_at
from models.schemas.list import *
from models.schemas.pagination import *
from utils.utils import db_query
from utils.helper import *


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


def _build_where_content(list_id: str, cursor: str | None, search: str | None, op: str | None) -> tuple[str, list]:
    """Constroi as clausular where para paginar os jogos de uma lista"""

    clauses = ["l.id = $1"]
    params = [list_id]

    if search is not None:
        params.append(escape_like(search) + "%")
        clauses.append(f"g.name ILIKE ${len(params)}")

    if cursor is not None:
        date, id = decode_cursor_to_tuple(cursor)
        params += [date, id]
        clauses.append(f"(lc.created_at, lc.game) {op} (${len(params)-1}, ${len(params)})")

    return "AND ".join(clauses), params


async def _DB_read_list_games_page(conn, list_id: str, page_query: PageQuery):
    """Lê uma página de games de uma lista retornando os jogos daquela página, quantos jogos pertencem à pagina
    e o cursor para acessar a próxima página"""

    size = page_query.page_size
    cursor = page_query.cursor
    search = page_query.search

    where, params = _build_where_content(list_id, cursor, search, ">")
    params.append(size+1)

    rows = await conn.fetch(f'''
        SELECT g.id, g.name, g.picture, g.year, lc.created_at
            COUNT(r.liked) FILTER (WHERE r.liked = true) AS like_count,
            COALESCE(ROUND(AVG(r.rating_num) FILTER (WHERE r.is_private = false)::numeric, 2), -1) AS gamerboxd_rating
        FROM Games g
        LEFT JOIN ListContent lc ON lc.game = g.id
        LEFT JOIN Reviews r ON r.game = g.id
        WHERE {where}
        ORDER BY lc.created_at ASC, lc.game ASC
        GROUP BY g.id, g.name, g.picture, g.year, lc.created_at
        LIMIT ${len(params)}
    ''', *params)

    has_more = len(rows) > size
    rows = list(rows[:size])

    next_cursor = encode_tuple_to_cursor(rows[-1]["created_at"], rows[-1]["id"]) if has_more else None
    games = [Game(
        game_id = r["id"],
        name = r["game"],
        picture = r["picture"],
        year = r["year"],
        like_count = r["like_count"],
        gamerboxd_rating = r["gamerboxd_rating"],
    ) for r in rows]

    return games, len(rows), next_cursor


async def _DB_read_list_games_previous_cursor(conn, list_id, page_query: PageQuery):
    """Retorna o cursor para voltar atrás uma página"""

    size = page_query.page_size
    cursor = page_query.cursor
    search = page_query.search

    if cursor is None:
        return None

    where, params = _build_where_content(list_id, cursor, search, "<")
    params.append(size+1)

    rows = await conn.fetch(f'''
        SELECT lc.game, lc.created_at
        LEFT JOIN ListContent lc ON lc.game = g.id
        WHERE {where}
        ORDER BY lc.created_at DESC, lc.game DESC
        LIMIT ${len(params)}
    ''', *params)

    has_more = len(rows) > size
    rows = list(rows[:size])

    prev_cursor = encode_tuple_to_cursor(rows[-1]["created_at"], rows[-1]["game"]) if has_more else None

    return prev_cursor

async def _DB_read_count_list_games(conn, list_id: str, search: str | None):
    """Conta quantos jogos pertencem a uma lista e correspondem a busca, se ela existir"""

    where, params = _build_where_content(list_id, None, search, None)

    return await conn.fetchval(f'''
        SELECT COUNT(*)
        LEFT JOIN ListContent lc ON lc.game = g.id
        WHERE {where}
    ''', *params)
    

@db_query
async def DB_read_list_games(conn, list_id: str, page_query: PageQuery):
    """Busca alguns dos jogos de uma lista"""

    async with conn.transaction():
        games, page_size, next_cursor = await _DB_read_list_games_page(conn, list_id, page_query)
        prev_cursor = await _DB_read_list_games_previous_cursor(conn, list_id, page_query)
        total_games = await _DB_read_count_list_games(conn, list_id, page_query.search)

    page_result = PageResult(content=games, current=page_query.cursor, total=total_games)
    page_result.page_size = page_size
    page_result.previous_page = prev_cursor
    page_result.next_page = next_cursor

    return page_result






