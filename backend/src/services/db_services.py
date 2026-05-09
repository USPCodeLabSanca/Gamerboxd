from uuid import uuid4

from models.schemas import *
from utils.db import DB_Result
from utils.helper import fix_date


async def DB_create_user(conn, user: UserIn):

    user_id = str(uuid4())

    try:
        await conn.execute('''
            INSERT INTO Users(user_id, username, email, password, bio, pfp)
            VALUES($1, $2, $3, $4, $5, $6)
        ''', user_id, user.username, user.email, user.password, user.bio, user.pfp)
        
    except Exception as e:
        return DB_Result(success=False, error=e)
    
    else:
        return DB_Result(success=True, message="Usuário criado com sucesso!", obj=user_id)
    

async def DB_create_list(conn, game_list: List):
        
    list_id = str(uuid4())

    try:
        await conn.execute('''
            INSERT INTO Lists(list_id, list_name, list_description, list_creator, is_private)
            VALUES($1, $2, $3, $4, $5)
        ''', list_id, game_list.name, game_list.description, game_list.creator, game_list.is_private)

        return DB_Result(success=True, message="Lista criada com sucesso!", obj=list_id)
    
    except Exception as e:
        return DB_Result(success=False, error=e)


async def DB_create_user_tags(conn, user_id, tag_name):
    try:
        tag_id = await conn.fetchval('SELECT tag_id FROM Tags WHERE tag_name = $1', tag_name)

        await conn.execute('INSERT INTO UserTags (user_a, tag) VALUES($1, $2)', user_id, tag_id)

        return DB_Result(success=True, message="Tag do usuário salva com sucesso!")

    except Exception as e:
        return DB_Result(success=False, error=e)


async def DB_create_saved_list(conn, list_id: str, user_id: str):
    try:
        await conn.execute('''
            INSERT INTO SavedLists(user_a, list) VALUES($1, $2)
        ''', user_id, list_id)

        return DB_Result(success=True, message="Lista salva com sucesso!", obj=list_id)
    
    except Exception as e:
        return DB_Result(success=False, error=e)
    

async def DB_create_follow(conn, user_follower: str, user_followed:str):
    try:
        await conn.execute('''
            INSERT INTO Follows(user_a, user_b) VALUES($1, $2)
        ''', user_follower, user_followed)

        return DB_Result(success=True, message="Novo seguidor cadastrado com sucesso!")
    
    except Exception as e:
        return DB_Result(success=False, error=e)
    

async def DB_delete_follow(conn, user_follower: str, user_followed:str):
    try:
        await conn.execute('''DELETE FROM Follows WHERE user_a = $1 AND user_b = $2', 
         ''', user_follower, user_followed)
    
        return DB_Result(success=True, message="Novo desseguidor cadastrado com sucesso!")
    
    except Exception as e:
        return DB_Result(success=False, error=e)
    


async def DB_read_user_column(conn, column: str, user_id: str = None, email: str = None, username: str = None):
    if username == None and user_id == None and email == None:
        raise TypeError("username, email e user_id não podem estar todos vazios")

    try:
        column_result = None

        if (user_id) and (column_result is None):
            column_result = await conn.fetchval(f"SELECT {column} FROM Users WHERE user_id = $1", user_id)

        if (email) and (column_result is None):
            column_result = await conn.fetchval(f"SELECT {column} FROM Users WHERE email = $1", email)

        if (username) and (column_result is None):
            column_result = await conn.fetchval(f"SELECT {column} FROM Users WHERE username = $1", username)
        
        if column_result is None:
            return DB_Result(
            success=True, 
            message="Usuário não existe",
            obj=None
        )
        
        return DB_Result(
            success=True, 
            message=f"{column} do usuário encontrado com sucesso!",
            obj=column_result
        )
        
    except Exception as e:
        return DB_Result(success=False, error = e)
    

async def DB_read_user_out(conn, user_id: str):
    
    try:
        row = await conn.fetchrow(
            """
            SELECT username, pfp, email, bio, created_at
            FROM Users
            WHERE user_id = $1
            """,
            user_id
        )

        if not row:
            raise ValueError("Não encontramos os dados do usuário")
 
        user = UserOut(
            username=row["username"],
            pfp=row["pfp"],
            email=row["email"],
            bio=row["bio"],
            created_at=fix_date(row["created_at"]),
        )

        return DB_Result(success=True, message="Dados do usuário encontrados!", obj=user)
    
    except Exception as e:
        return DB_Result(success=False, error=e)


async def DB_read_user_follows(conn, user_id: str):
    
    try:
        follower_rows = await conn.fetch(
            """
            SELECT u.username, u.pfp
            FROM Follows f
            JOIN Users u ON u.user_id = f.user_a
            WHERE f.user_b = $1
            """,
            user_id,
        )
        following_rows = await conn.fetch(
            """
            SELECT u.username, u.pfp
            FROM Follows f
            JOIN Users u ON u.user_id = f.user_b
            WHERE f.user_a = $1
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
        
        return DB_Result(success=True, message="Relações do usuário encontradas", obj=user_follows)
        
    except Exception as e:
        print("MUUUUUUUU7")
        return DB_Result(success=False, error=e)


async def DB_read_user_lists(conn, user_id: str):
    
    try:
        rows = await conn.fetch(
            """
            SELECT l.list_name, l.list_description, u.username AS list_creator, l.is_private, l.created_at,
            COUNT(sl2.user_a) AS list_saves
            FROM SavedLists sl
            JOIN Lists l ON l.list_id = sl.list
            JOIN Users u ON u.user_id = l.list_creator
            LEFT JOIN SavedLists sl2 ON sl2.list = sl.list
            WHERE sl.user_a = $1
            GROUP BY l.list_name, l.list_description, u.username, l.is_private, l.created_at
            """,
            user_id,
        )
 
        lists = [
            ListFull(
                name=r["list_name"],
                description=r["list_description"],
                creator=r["list_creator"],
                is_private=r["is_private"],
                created_at=fix_date(r["created_at"]),
                list_saves=r["list_saves"],
            )
            for r in rows
        ]
 
        user_lists = UserLists(list_count=len(lists), lists=lists)

        return DB_Result(success=True, message="Listas salvas pelo usuário encontrados!", obj=user_lists)
        
    except Exception as e:
        return DB_Result(success=False, error=e)


async def DB_read_user_tags(conn, user_id: str = None):

    try:
        rows = await conn.fetch(
            """
            SELECT t.tag_name
            FROM UserTags ut
            JOIN Tags t ON t.tag_id = ut.tag
            WHERE ut.user_a = $1
            """,
            user_id,
        )
 
        tags = [r["tag_name"] for r in rows]
        user_tags = UserTags(tag_count=len(tags), tags=tags)

        return DB_Result(success=True, message="Listas salvas pelo usuário encontrados!", obj=user_tags)
        
    except Exception as e:
        return DB_Result(success=False, error=e)