from uuid import uuid4

from models.schemas import *
from utils.db import DB_Result


async def DB_create_account(conn, user: User):

    user_id = str(uuid4())

    try:
        await conn.execute('''
            INSERT INTO Users(user_id, username, email, password, bio, pfp)
            VALUES($1, $2, $3, $4, $5, $6)
        ''', user_id, user.username, user.email, user.password, user.bio, user.pfp)
        
    except Exception as e:
        return DB_Result(success=False, message=str(e))
    
    else:
        return DB_Result(success=True, message="Usuário criado com sucesso!", obj=user_id)
    
async def DB_create_list(conn, game_list: List):
        
    list_id = str(uuid4())
    try:
        await conn.execute('''
            INSERT INTO Lists(list_id, list_name, list_description, list_creator, is_private)
            VALUES($1, $2, $3, $4, $5)
        ''', list_id, game_list.name, game_list.description, game_list.creator, game_list.is_private)

    
    except Exception as e:
        return DB_Result(success=False, message=str(e))
    
    else:
        return DB_Result(success=True, message="Lista criada com sucesso!", obj=list_id)
    

async def DB_read_user_cred(conn, user: Auth_login):

    try:
        row = await conn.fetchrow('''
            SELECT user_id, password FROM Users WHERE email = $1 OR username = $1
        ''', user.email_or_username,)
        
        if not row:
            raise ValueError("Não existe esse usuário!")
        
    except Exception as e:
        return DB_Result(success=False, message=str(e))
    
    else:
        return DB_Result(
            success=True, 
            message="Credenciais do usuário encontradas com sucesso!",
            obj={"user_id":row[0], "password": row[1]}
            )
    
async def DB_read_username_already_exists(conn, user: User):
    try:
        username = await conn.fetchval('''
            SELECT username FROM Users WHERE username = $1
        ''', user.username)

    except Exception as e:
        return DB_Result(success=False, message=str(e))
    
    else:
        return DB_Result(
            success=True, 
            message="Busca na tabela de usuários não apresentou erros",
            obj=(username == user.username)
            ) 

async def DB_read_email_already_exists(conn, user: User):
    try:
        email = await conn.fetchval('''
            SELECT email FROM Users WHERE email = $1
        ''', user.email)

    except Exception as e:
        return DB_Result(success=False, message=str(e))
    
    else:
        return DB_Result(
            success=True, 
            message="Busca na tabela de usuários não apresentou erros",
            obj=(email == user.email)
        )         