from uuid import uuid4

from models.schemas.user import *
from utils import *


@db_query
async def DB_create_user(conn, user: UserIn):
    user_id = str(uuid4())
    await conn.execute('''
        INSERT INTO Users(id, username, email, password)
        VALUES($1, $2, $3, $4)
    ''', user_id, user.username, user.email, user.password)
    
    return user_id


@db_query
async def DB_delete_user(conn, user_id: str):
    await conn.execute('''
        DELETE FROM Users
        WHERE id = $1
    ''', user_id)


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
        SELECT username, pfp, bio, created_at
        FROM Users
        WHERE id = $1
    ''', user_id)

    if row is None:
        return None

    user = UserOut(
        user_id=user_id,
        username=row["username"],
        pfp=row["pfp"],
        bio=row["bio"],
        created_at=fix_date(row["created_at"]),
    )

    return user


@db_query
async def DB_update_user(conn, user: UserEdit, user_id: str):
    await conn.execute('''
        UPDATE Users 
        SET username = $1, email = $2, bio = $3 , pfp = $4
        WHERE id = $5
    ''', user.username, user.email, user.bio, user.pfp, user_id)

    return user

