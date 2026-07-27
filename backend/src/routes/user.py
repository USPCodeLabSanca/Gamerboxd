from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from models.schemas.user import *
from services.security_services import is_user_valid, encrypt_password, encode_token
from services.db_services.user import *
from services.db_services.list import *
from utils.dependencies import get_conn, require_login, get_key
from utils.utils import QueryError

user_router = APIRouter(prefix="/user", tags=["user"])

@user_router.post("/")
async def new_user(user: UserIn, conn = Depends(get_conn), key = Depends(get_key)):

    # Validação do username, email e senha
    user = await is_user_valid(user, conn)     
    user.password = encrypt_password(user.password)

    new_user_id = await DB_create_user(conn, user)

    # Cria e salva as listas de favoritos e de completados
    await first_lists(new_user_id, conn)
    
    new_access_token = encode_token(new_user_id, 10, key)
    new_refresh_token = encode_token(new_user_id, 1440, key)

    response = JSONResponse({"message":"Conta criada com sucesso!"})
    response.set_cookie("access-token", new_access_token, secure=True, httponly=True)
    response.set_cookie("refresh-token", new_refresh_token, secure=True, httponly=True)
    
    return response


async def first_lists(user_id, conn):
    async with conn.transaction():

        # Cria a lista de favoritos
        favorites_list = List(
            creator = user_id,
            name = "Favoritos",
            description = "Meus games favoritos",
            is_private = True
        )
        
        favorites_list_id = await DB_create_list(conn, favorites_list)
            
        # Cria a lista de completados
        finished_list = List(
            creator = user_id,
            name = "Completados",
            description = "Meus games completados",
            is_private = True
        )

        finished_list_id = await DB_create_list(conn, finished_list)
        
        # Salva a lista de favoritos e completados
        await DB_create_list_save(conn, favorites_list_id, user_id)
        await DB_create_list_save(conn, finished_list_id, user_id)


async def get_full(conn, user_id): 
    out = await DB_read_user_out(conn, user_id)       
    follows = await DB_read_user_follows(conn, user_id)
    lists = await DB_read_user_lists(conn, user_id)

    user_full = UserFull(
        username=out.username,
        pfp=out.pfp,
        email=out.email,
        bio=out.bio,
        created_at=out.created_at,
        lists=lists,
        follows=follows
    )

    return user_full


@user_router.get("/")
async def see_my_account(conn = Depends(get_conn), user_id = Depends(require_login)):    
    user_full = await get_full(conn, user_id)

    return JSONResponse(user_full.model_dump())


@user_router.get("/view/{username}")
async def see_account(username: str, conn = Depends(get_conn)):
    user_id = await DB_read_user_column(conn, "user_id", username=username)

    if user_id is None:
        raise QueryError(404, "Usuário não encontrado!")

    user_full = await get_full(conn, user_id)

    return JSONResponse(user_full.model_dump())


#VERIFICAR SE NÃO FOI BLOQUEADO!!!
@user_router.post("/follow/{username}")
async def follow(username: str, conn = Depends(get_conn), user_id = Depends(require_login)):
    user_id_to_follow = await DB_read_user_column(conn, "user_id", username=username)
    
    if user_id_to_follow is None:
        raise QueryError(404, "Usuário não encontrado!")
        
    await DB_create_follow(conn, user_id, user_id_to_follow)

    return JSONResponse({"message":"Conta seguida com sucesso!"})


@user_router.post("/unfollow/{username}")
async def unfollow(username: str, conn = Depends(get_conn), user_id = Depends(require_login)):
    user_id_to_unfollow = await DB_read_user_column(conn, "user_id", username=username)
    
    if user_id_to_unfollow is None:
        raise QueryError(404, "Usuário não encontrado!")
        
    await DB_delete_follow(conn, user_id, user_id_to_unfollow)

    return JSONResponse({"message":"Conta desseguida com sucesso!"})
    

@user_router.put("/")
async def edit_user(user: UserEdit, conn = Depends(get_conn), user_id = Depends(require_login)):
    user = await is_user_valid(user, conn)
    await DB_update_user(conn, user, user_id)
    user_full = await get_full(conn, user_id)

    return JSONResponse(user_full.model_dump())


@user_router.delete("/")
async def delete_user(user_id = Depends(require_login), conn = Depends(get_conn)):
    await DB_delete_user(conn, user_id)

    return JSONResponse({"message":"Conta deletada com sucesso!"})

# Remover dos seguidores!    
@user_router.post("/block/{username}")
async def block_user(username: str, user_id = Depends(require_login), conn = Depends(get_conn)):
    user_id_to_block = await DB_read_user_column(conn, "user_id", username=username)

    if user_id_to_block is None:
        raise QueryError(404, "Usuário não encontrado!")

    await DB_create_block(conn, user_id, user_id_to_block)

    return JSONResponse({"message":"Conta bloqueada com sucesso!"})


@user_router.post("/unblock/{username}")
async def unblock_user(username: str, user_id = Depends(require_login), conn = Depends(get_conn)):

    user_id_to_unblock = await DB_read_user_column(conn, "user_id", username=username)
        
    if user_id_to_unblock is None:
        raise QueryError(404, "Usuário não encontrado!")

    await DB_delete_block(conn, user_id, user_id_to_unblock)

    return JSONResponse({"message":"Conta desbloqueada com sucesso!"})