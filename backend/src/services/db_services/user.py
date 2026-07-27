from uuid import uuid4

from models.schemas.user import *
from utils.utils import db_query
from utils.helper import fix_date


@db_query
async def DB_create_user(conn, user: UserIn):
    user_id = str(uuid4())
    await conn.execute('''
        INSERT INTO Users(user_id, username, email, password)
        VALUES($1, $2, $3, $4)
    ''', user_id, user.username, user.email, user.password)
    
    return user_id


@db_query
async def DB_create_follow(conn, user_follower: str, user_followed: str):
    await conn.execute('''
        INSERT INTO Follows(user_a, user_b) VALUES($1, $2)
    ''', user_follower, user_followed)


@db_query
async def DB_create_block(conn, user_a: str, user_b: str):
    await conn.execute('''
        INSERT INTO Blocks(user_a, user_b) VALUES($1, $2)
    ''', user_a, user_b)


@db_query
async def DB_delete_user(conn, user_id: str):
    await conn.execute('''
        DELETE FROM Users WHERE user_id = $1
    ''', user_id)


@db_query    
async def DB_delete_follow(conn, user_follower: str, user_followed: str):
    await conn.execute('''
            DELETE FROM Follows WHERE user_a = $1 AND user_b = $2', 
        ''', user_follower, user_followed)


@db_query
async def DB_delete_block(conn, user_a: str, user_b: str):
    await conn.execute('''
        DELETE FROM Blocks WHERE user_a = $1 AND user_b = $2
    ''', user_a, user_b)


@db_query
async def DB_read_user_column(conn, column: str, user_id: str = None, email: str = None, username: str = None):
    if username == None and user_id == None and email == None:
        raise TypeError("username, email e user_id não podem estar todos vazios")

    column_result = None

    if (user_id) and (column_result is None):
        column_result = await conn.fetchval(f"SELECT {column} FROM Users WHERE user_id = $1", user_id)

    if (email) and (column_result is None):
        column_result = await conn.fetchval(f"SELECT {column} FROM Users WHERE email = $1", email)

    if (username) and (column_result is None):
        column_result = await conn.fetchval(f"SELECT {column} FROM Users WHERE username = $1", username)
    
    return column_result


@db_query
async def DB_read_user_out(conn, user_id: str):
    row = await conn.fetchrow(
        """
        SELECT username, pfp, email, bio, created_at
        FROM Users
        WHERE user_id = $1
        """,
        user_id
    )

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
    follower_rows = await conn.fetch(
        """
        SELECT u.username, u.pfp
        FROM Follows f
        JOIN Users u ON u.user_id = f.user_a
        WHERE f.user_b = $1
        ORDER BY f.created_at DESC
        """,
        user_id,
    )
    
    following_rows = await conn.fetch(
        """
        SELECT u.username, u.pfp
        FROM Follows f
        JOIN Users u ON u.user_id = f.user_b
        WHERE f.user_a = $1
        ORDER BY f.created_at DESC
        """,
        user_id,
    )

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
async def DB_update_user(conn, user: UserEdit, user_id: str):

    await conn.execute('''
        UPDATE Users 
        SET username = $1, email = $2, bio = $3 , pfp = $4
        WHERE user_id = $5
    ''', user.username, user.email, user.bio, user.pfp, user_id)

    return user
    
