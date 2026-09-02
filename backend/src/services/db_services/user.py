from uuid import uuid4

from models.schemas.user import *
from utils.utils import db_query
from utils.helper import fix_date


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
        ON CONFLICT
        DO NOTHING
    ''', user_follower, user_followed)


@db_query
async def DB_create_block(conn, user_blocker: str, user_blocked:str):
    await conn.execute('''
        INSERT INTO Blocks(blocker, blocked)
        VALUES($1, $2)
        ON CONFLICT
        DO NOTHING
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


@db_query
async def DB_read_user_follows(conn, user_id: str):
    follower_rows = await conn.fetch('''
        SELECT u.username, u.pfp
        FROM Follows f
        JOIN Users u ON u.id = f.follower
        WHERE f.followed = $1
        ORDER BY f.created_at DESC
    ''', user_id)
    
    following_rows = await conn.fetch('''
        SELECT u.username, u.pfp
        FROM Follows f
        JOIN Users u ON u.id = f.followed
        WHERE f.follower = $1
        ORDER BY f.created_at DESC
    ''', user_id)

    followers = [User(username=r["username"], pfp=r["pfp"]) for r in follower_rows]
    followings = [User(username=r["username"], pfp=r["pfp"]) for r in following_rows]

    user_follows = UserFollows(
        follower_count=len(followers),
        followers=followers,
        following_count=len(followings),
        followings=followings
    )
    
    return user_follows

@db_query
async def DB_read_user_blockeds(conn, user_id: str):
    blockeds = await conn.fetch('''
        SELECT blocked FROM Blocks
        WHERE blocker = $1
    ''', user_id)

    return blockeds

@db_query
async def DB_read_user_blockeds_full(conn, user_id: str):
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
    
