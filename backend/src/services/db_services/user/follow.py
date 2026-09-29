from models.schemas.user import *
from models.schemas.pagination import *
from utils.utils import db_query
from utils.helper import *


@db_query
async def DB_create_follow(conn, user_follower: str, user_followed: str):
    await conn.execute('''
        INSERT INTO Follows(follower, followed)
        VALUES($1, $2)
    ''', user_follower, user_followed)


@db_query    
async def DB_delete_follow(conn, user_follower: str, user_followed: str):
    await conn.execute('''
        DELETE FROM Follows
        WHERE follower = $1 AND followed = $2 
    ''', user_follower, user_followed)


def _build_where_follow(user_id: str, owner_col: str, other_col: str, cursor: str, search: str | None, op: str) -> tuple[str, list]:
    params = [user_id]
    clauses = [f"f.{owner_col} = $1"]

    if search is not None:
        params.append(escape_like(search) + "%")
        clauses.append(f"u.username ILIKE ${len(params)}")

    if cursor is not None:
        cursor_date, cursor_id = decode_cursor_to_tuple(cursor)
        params += [cursor_date, cursor_id]
        clauses.append(
            f"(f.created_at, f.{other_col}) {op} (${len(params)-1}, ${len(params)})"
        )

    return " AND ".join(clauses), params


async def _DB_read_follow_page(conn, user_id: str, page_query: PageQuery, owner_col: str, other_col: str) -> PageResult:

    size = page_query.page_size
    cursor = page_query.cursor
    search = page_query.search

    where, params = _build_where_follow(user_id, owner_col, other_col, cursor, search, "<")
    params.append(size+1)

    rows = await conn.fetch(f'''
        SELECT u.id, u.username, u.pfp, f.created_at
        FROM Follows f
        JOIN Users u ON u.id = f.{other_col}
        WHERE {where}
        ORDER BY f.created_at DESC, f.{other_col} DESC
        LIMIT ${len(params)}
    ''', *params)

    has_more = len(rows) > size
    rows = list(rows[:size])

    next_cursor = encode_tuple_to_cursor(rows[-1]["created_at"], rows[-1]["id"]) if has_more else None
    relationships = [User(username=r["username"], pfp=r["pfp"]) for r in rows]

    return relationships, len(rows), next_cursor


async def _DB_read_follow_previous_cursor(conn, user_id: str, page_query: PageQuery, owner_col: str, other_col: str) -> PageResult:
    size = page_query.page_size
    cursor = page_query.cursor
    search = page_query.search

    if cursor is None:
        return None
    
    where, params = _build_where_follow(user_id, owner_col, other_col, cursor, search, ">")
    params.append(size+1)

    rows = await conn.fetch(f'''
            SELECT f.{other_col} AS id, f.created_at
            FROM Follows f
            WHERE {where}
            ORDER BY f.created_at ASC, f.{other_col} ASC
            LIMIT ${len(params)}
        ''', *params)

    has_more = len(rows) > size
    rows = list(rows[:size])

    prev_cursor = encode_tuple_to_cursor(rows[-1]["created_at"], rows[-1]["id"]) if has_more else None

    return prev_cursor



async def _DB_read_count_follow(conn, user_id: str, owner_col: str, other_col: str, search: str | None):

    where, params = _build_where_follow(user_id, owner_col, other_col, None, search, None)
    return await conn.fetchval(f'''
        SELECT COUNT(*)
        FROM Follows f
        JOIN Users u ON u.id = f.{other_col}
        WHERE {where}
    ''', *params)


@db_query
async def DB_read_user_followers(conn, user_id: str, page_query: PageQuery):

    async with conn.transaction():
        followers, page_size, next_cursor = await _DB_read_follow_page(conn, user_id, page_query, "followed", "follower")
        prev_cursor = await _DB_read_follow_previous_cursor(conn, user_id, page_query, "followed", "follower")
        total_followers = await _DB_read_count_follow(conn, user_id, "followed", "follower", page_query.search)

    page_result = PageResult(content=followers, total=total_followers, current=page_query.cursor)
    page_result.page_size = page_size
    page_result.previous_page = prev_cursor
    page_result.next_page = next_cursor

    return page_result


@db_query
async def DB_read_user_followeds(conn, user_id: str, page_query: PageQuery):

    async with conn.transaction():
        followeds, page_size, next_cursor = await _DB_read_follow_page(conn, user_id, page_query, "follower", "followed")
        prev_cursor = await _DB_read_follow_previous_cursor(conn, user_id, page_query, "follower", "followed")
        total_followeds = await _DB_read_count_follow(conn, user_id, "follower", "followed", page_query.search)

    page_result = PageResult(content=followeds, total=total_followeds, current=page_query.cursor)
    page_result.page_size = page_size
    page_result.previous_page = prev_cursor
    page_result.next_page = next_cursor

    return page_result


@db_query
async def DB_read_user_follows(conn, user_id: str):
    total_followers = await _DB_read_count_follow(conn, user_id, "followed", "follower", None)
    total_followeds = await _DB_read_count_follow(conn, user_id, "follower", "follower", None)

    return UserFollows(follower_count=total_followers, following_count=total_followeds)