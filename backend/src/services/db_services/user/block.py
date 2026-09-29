from models.schemas.user import *
from models.schemas.pagination import *
from utils.utils import db_query
from utils.helper import *


@db_query
async def DB_create_block(conn, user_blocker: str, user_blocked:str):
    await conn.execute('''
        INSERT INTO Blocks(blocker, blocked)
        VALUES($1, $2)
    ''', user_blocker, user_blocked)


@db_query
async def DB_delete_block(conn, user_blocker: str, user_blocked:str):
    await conn.execute('''
        DELETE FROM Blocks
        WHERE blocker = $1 AND blocked = $2
    ''', user_blocker, user_blocked)


def _build_where_block(user_id: str, cursor: str, search: str | None, op: str) -> tuple[str, list]:
    params = [user_id]
    clauses = [f"b.blocker = $1"]

    if search is not None:
        params.append(escape_like(search) + "%")
        clauses.append(f"u.username ILIKE ${len(params)}")

    if cursor is not None:
        cursor_date, cursor_id = decode_cursor_to_tuple(cursor)
        params += [cursor_date, cursor_id]
        clauses.append(
            f"(b.created_at, b.blocked) {op} (${len(params)-1}, ${len(params)})"
        )

    return " AND ".join(clauses), params


async def _DB_read_block_page(conn, user_id: str, page_query: PageQuery) -> PageResult:

    size = page_query.page_size
    cursor = page_query.cursor
    search = page_query.search

    where, params = _build_where_block(user_id, cursor, search, "<")
    params.append(size+1)

    rows = await conn.fetch(f'''
        SELECT u.id, u.username, u.pfp, b.created_at
        FROM Blocks b
        JOIN Users u ON u.id = b.blocked
        WHERE {where}
        ORDER BY b.created_at DESC, b.blocked DESC
        LIMIT ${len(params)}
    ''', *params)

    has_more = len(rows) > size
    rows = list(rows[:size])

    next_cursor = encode_tuple_to_cursor(rows[-1]["created_at"], rows[-1]["id"]) if has_more else None
    blocks = [User(username=r["username"], pfp=r["pfp"]) for r in rows]

    return blocks, len(rows), next_cursor


async def _DB_read_block_previous_cursor(conn, user_id: str, page_query: PageQuery) -> PageResult:
    size = page_query.page_size
    cursor = page_query.cursor
    search = page_query.search

    if cursor is None:
        return None
    
    where, params = _build_where_block(user_id, cursor, search, ">")
    params.append(size+1)

    rows = await conn.fetch(f'''
            SELECT b.blocked AS id, f.created_at
            FROM Blocks b
            WHERE {where}
            ORDER BY b.created_at ASC, b.blocked ASC
            LIMIT ${len(params)}
        ''', *params)

    has_more = len(rows) > size
    rows = list(rows[:size])

    prev_cursor = encode_tuple_to_cursor(rows[-1]["created_at"], rows[-1]["id"]) if has_more else None

    return prev_cursor


async def _DB_read_count_block(conn, user_id: str, search: str | None):

    where, params = _build_where_block(user_id, None, search, None)
    return await conn.fetchval(f'''
        SELECT COUNT(*)
        FROM Blocks b
        JOIN Users u ON u.id = b.blocker
        WHERE {where}
    ''', *params)


@db_query
async def DB_read_user_blockeds(conn, user_id: str, page_query: PageQuery):

    async with conn.transaction():
        blockeds, page_size, next_cursor = await _DB_read_block_page(conn, user_id, page_query)
        prev_cursor = await _DB_read_block_previous_cursor(conn, user_id, page_query)
        total_blockeds = await _DB_read_count_block(conn, user_id, page_query.search)

    page_result = PageResult(content=blockeds, total=total_blockeds, current=page_query.cursor)
    page_result.page_size = page_size
    page_result.previous_page = prev_cursor
    page_result.next_page = next_cursor

    return page_result


@db_query
async def DB_read_user_blocks(conn, user_id: str):
    total_blockeds = await _DB_read_count_block(conn, user_id, None)

    return UserBlocked(blocked_count=total_blockeds)
