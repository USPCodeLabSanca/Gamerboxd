from uuid import uuid4

from models.schemas.user import *
from models.schemas.pagination import *
from utils.utils import db_query, QueryError
from utils.helper import *


@db_query
async def DB_create_user(conn, user: UserIn):
    user_id = str(uuid4())
    await conn.execute('''
        INSERT INTO Users(id, username, email, password)
        VALUES($1, $2, $3, $4)
    ''', user_id, user.username, user.email, user.password)
    
    return user_id


@db_query
async def DB_create_follow(conn, user_follower: str, user_followed: str):
    await conn.execute('''
        INSERT INTO Follows(follower, followed)
        VALUES($1, $2)
    ''', user_follower, user_followed)


@db_query
async def DB_create_block(conn, user_blocker: str, user_blocked:str):
    await conn.execute('''
        INSERT INTO Blocks(blocker, blocked)
        VALUES($1, $2)
    ''', user_blocker, user_blocked)


@db_query
async def DB_delete_user(conn, user_id: str):
    await conn.execute('''
        DELETE FROM Users
        WHERE id = $1
    ''', user_id)


@db_query    
async def DB_delete_follow(conn, user_follower: str, user_followed: str):
    await conn.execute('''
        DELETE FROM Follows
        WHERE follower = $1 AND followed = $2 
    ''', user_follower, user_followed)


@db_query
async def DB_delete_block(conn, user_blocker: str, user_blocked:str):
    await conn.execute('''
        DELETE FROM Blocks
        WHERE blocker = $1 AND blocked = $2
    ''', user_blocker, user_blocked)


@db_query
async def DB_read_user_column(conn, column: str, user_id: str = None, email: str = None, username: str = None):
    if not any([x is not None for x in (username, user_id, email)]):
        raise TypeError("username, email e id não podem estar todos vazios")

    column_result = None

    if (user_id) and (column_result is None):
        column_result = await conn.fetchval(f"SELECT {column} FROM Users WHERE id = $1", user_id)

    if (email) and (column_result is None):
        column_result = await conn.fetchval(f"SELECT {column} FROM Users WHERE email = $1", email)

    if (username) and (column_result is None):
        column_result = await conn.fetchval(f"SELECT {column} FROM Users WHERE username = $1", username)
    
    return column_result


@db_query
async def DB_read_user_out(conn, user_id: str):
    row = await conn.fetchrow('''
        SELECT username, pfp, email, bio, created_at
        FROM Users
        WHERE id = $1
    ''', user_id)

    if row is None:
        return None

    user = UserOut(
        username=row["username"],
        pfp=row["pfp"],
        email=row["email"],
        bio=row["bio"],
        created_at=fix_date(row["created_at"]),
    )

    return user


async def _DB_read_follow_page(conn, user_id, page_query, owner_col, other_col):
    size = page_query.page_size
    cursor = page_query.cursor

    if cursor is not None:
        cursor_date, cursor_id = decode_cursor_to_tuple(cursor)
        where = f"AND (f.created_at, f.{other_col}) > ($2, $3)"
        params = [user_id, cursor_date, cursor_id, size+1]

    else:
        where = ""
        params = [user_id, size+1]

    rows = await conn.fetch(f'''
        SELECT u.id, u.username, u.pfp, f.created_at
        FROM Follows f
        JOIN Users u ON u.id = f.{other_col}
        WHERE f.{owner_col} = $1 {where}
        ORDER BY f.created_at DESC, f.{other_col} DESC
        LIMIT ${len(params)}
    ''', *params)

    has_more = len(rows) > size
    rows = list(rows)
    last_row = rows.pop()

    next_cursor = encode_tuple_to_cursor(last_row["created_at"], last_row["id"]) if has_more else None
    relationships = [User(username=r["username"], pfp=r["pfp"]) for r in rows]

    return relationships, len(rows), next_cursor


async def _DB_read_follow_previous_cursor(conn, user_id, page_query, owner_col, other_col):
    size = page_query.page_size
    cursor = page_query.cursor

    if cursor is not None:
        cursor_date, cursor_id = decode_cursor_to_tuple(cursor)
        where = f"AND (f.created_at, f.{other_col}) < ($2, $3)"
        params = [user_id, cursor_date, cursor_id, size+1]

    else:
        where = ""
        params = [user_id, size+1]

    rows = await conn.fetch(f'''
        SELECT u.id, f.created_at
        FROM Follows f
        JOIN Users u ON u.id = f.{other_col}
        WHERE f.{owner_col} = $1 {where}
        ORDER BY f.created_at ASC, f.{other_col} ASC
        LIMIT ${len(params)}
    ''', *params)

    has_more = len(rows) > size
    rows = list(rows)
    last_row = rows.pop()

    next_cursor = encode_tuple_to_cursor(last_row["created_at"], last_row["id"]) if has_more else None
    relationships = [User(username=r["username"], pfp=r["pfp"]) for r in rows]

    return relationships, len(rows), next_cursor


@db_query
async def DB_read_user_followers(conn, user_id: str, page_query: PageQuery):

    # Primeira busca, ainda não existe um cursor
    if page_query.cursor is None:
        follower_rows = await conn.fetch('''
            SELECT u.id, u.username, u.pfp, f.created_at
            FROM Follows f
            JOIN Users u ON u.id = f.follower
            WHERE f.followed = $1 
            ORDER BY f.created_at DESC, f.follower DESC
            LIMIT $2
        ''', user_id, page_query.page_size)
        prev = None
        last_row = follower_rows[-1]
        next = encode_tuple_to_cursor(last_row["created_at"], last_row["id"])

    else:
        date, followed_id = decode_cursor_to_tuple(page_query.cursor)
        follower_rows = await conn.fetch('''
            SELECT u.id, u.username, u.pfp, f.created_at
            FROM Follows f
            JOIN Users u ON u.id = f.follower
            WHERE f.followed = $1 AND (f.created_at, f.follower) > ($2, $3)
            ORDER BY f.created_at ASC, f.follower ASC
            LIMIT $4
        ''', user_id, date, followed_id, page_query.page_size + 1)
        first_row = follower_rows.pop(0)
        prev = encode_tuple_to_cursor(first_row["created_at"], first_row["id"])
        last_row = follower_rows[-1]
        next = encode_tuple_to_cursor(last_row["created_at"], last_row["id"])
        follower_rows.reverse()

    followers = [User(username=r["username"], pfp=r["pfp"]) for r in follower_rows]
    
    return prev, next, followers


@db_query
async def DB_read_user_followeds(conn, user_id: str, page_query: PageQuery):

    # Primeira busca, ainda não existe um cursor
    if page_query.cursor is None:
        followed_rows = await conn.fetch('''
            SELECT u.id, u.username, u.pfp, f.created_at
            FROM Follows f
            JOIN Users u ON u.id = f.followed
            WHERE f.follower = $1 
            ORDER BY f.created_at DESC, f.followed DESC
            LIMIT $2
        ''', user_id, page_query.page_size)
        prev = None
        last_row = followed_rows[-1]
        next = encode_tuple_to_cursor(last_row["created_at"], last_row["id"])

    else:
        date, follower_id = decode_cursor_to_tuple(page_query.cursor)
        followed_rows = await conn.fetch('''
            SELECT u.id, u.username, u.pfp, f.created_at
            FROM Follows f
            JOIN Users u ON u.id = f.followed
            WHERE f.follower = $1 AND (f.created_at, f.followed) > ($2, $3)
            ORDER BY f.created_at ASC, f.followed ASC
            LIMIT $4
        ''', user_id, date, follower_id, page_query.page_size + 1)

        first_row = followed_rows.pop(0)
        prev = encode_tuple_to_cursor(first_row["created_at"], first_row["id"])
        last_row = followed_rows[-1]
        next = encode_tuple_to_cursor(last_row["created_at"], last_row["id"])
        followed_rows.reverse()

    followeds = [User(username=r["username"], pfp=r["pfp"]) for r in followed_rows]
    
    return prev, next, followeds

@db_query
async def DB_read_user_blockeds(conn, user_id: str):
    blocked_rows = await conn.fetch('''
        SELECT u.username, u.pfp
        FROM Blocks b
        JOIN Users u ON u.id = b.blocked
        WHERE b.blocker = $1
        ORDER BY b.created_at DESC
    ''', user_id)

    blockeds = [User(username=r["username"], pfp=r["pfp"]) for r in blocked_rows]

    user_blockeds = UserBlocked(
        blocked_count=len(blockeds),
        blocks = blockeds
    )
    return user_blockeds
    

@db_query
async def DB_update_user(conn, user: UserEdit, user_id: str):
    await conn.execute('''
        UPDATE Users 
        SET username = $1, email = $2, bio = $3 , pfp = $4
        WHERE id = $5
    ''', user.username, user.email, user.bio, user.pfp, user_id)

    return user
    
