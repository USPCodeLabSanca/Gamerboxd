from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from models.schemas.user import *
from services.security_services import is_user_valid, encrypt_password, encode_token, is_blocked
from services.db_services.user import *
from services.db_services.list import *
from utils.dependencies import get_conn, require_login, get_key, optional_login
from utils.utils import QueryError

user_router = APIRouter(prefix="/user", tags=["user"])

@user_router.post("/")
async def new_user(user: UserIn, conn = Depends(get_conn), key = Depends(get_key)):
    """ Cria uma nova conta de usuário. Ao criar a conta, 2 listas padrão são geradas (Favoritos e Completados)"""

    async with conn.transaction():
        user = await is_user_valid(user, conn, None)    # Validação do username, email e senha
        user.password = encrypt_password(user.password) # Encriptação da senha  
        new_user_id = await DB_create_user(conn, user)  # Adiciona ao BD
        await first_lists(new_user_id, conn)            # Cria e salva as listas de favoritos e de completados

    # Loga o usuário
    response = JSONResponse({"message":"Conta criada com sucesso!"})
    new_access_token = encode_token(new_user_id, 10, key)
    new_refresh_token = encode_token(new_user_id, 1440, key)
    response.set_cookie("access-token", new_access_token, secure=True, httponly=True)
    response.set_cookie("refresh-token", new_refresh_token, secure=True, httponly=True)
    
    return response


async def first_lists(user_id, conn):
    """Cria as listas padrão de todo usuário: Favoritos e Completados"""

    # Cria e salva a lista de favoritos
    favorites_list = List(
        creator = user_id,
        name = "Favoritos",
        description = "Meus games favoritos",
        is_private = True
    )
    
    favorites_list_id = await DB_create_list(conn, favorites_list)
    await DB_create_list_save(conn, favorites_list_id, user_id)
        
    # Cria e salva a lista de completados
    finished_list = List(
        creator = user_id,
        name = "Completados",
        description = "Meus games completados",
        is_private = True
    )

    finished_list_id = await DB_create_list(conn, finished_list)
    await DB_create_list_save(conn, finished_list_id, user_id)


async def get_full(conn, user_id): 
    """Lê os dados completos de uma conta de usuário"""

    out = await DB_read_user_out(conn, user_id) # Dados da conta do usuário     
    follows = await DB_read_user_follows(conn, user_id) # Dados de seguidores do usuário
    lists = await DB_read_user_saved_lists(conn, user_id) # Dados das listas salvas pelo usuário

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
    """Retorna os dados completos do usuário autenticado"""

    user_full = await get_full(conn, user_id)
    return JSONResponse(user_full.model_dump())


@user_router.get("/{username}")
async def see_account(username: str, conn = Depends(get_conn), user_id = Depends(optional_login)):
    """Retorna os dados públicos de qualquer usuário pelo username"""

    target_user_id = await DB_read_user_column(conn, "id", username=username)  

    if (user_id is not None) and (await is_blocked(conn, target_user_id, user_id)):
        raise QueryError(403, "Usuário está tentando ver a conta que alguém que o bloqueou!")
        
    if target_user_id is None:
        raise QueryError(404, "Usuário não encontrado!")

    user_full = await get_full(conn, target_user_id)

    return JSONResponse(user_full.model_dump())
    

@user_router.put("/")
async def edit_user(user: UserEdit, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Atualiza os dados do usuário autenticado"""

    async with conn.transaction():
        user = await is_user_valid(user, conn, user_id) # Validação do username, email e senha
        await DB_update_user(conn, user, user_id)   # Atualiza o usuário no BD
        user_full = await get_full(conn, user_id)   # Busca os dados atualizados do usuário

    return JSONResponse(user_full.model_dump())


@user_router.delete("/")
async def delete_user(conn = Depends(get_conn), user_id = Depends(require_login)):
    """Remove permanentemente a conta do usuário autenticado"""

    await DB_delete_user(conn, user_id)
    return JSONResponse({"message":"Conta deletada com sucesso!"})


@user_router.post("/follow/{username}")
async def follow(username: str, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Faz o usuário autenticado seguir outro usuário"""

    user_id_to_follow = await DB_read_user_column(conn, "id", username=username)
    
    if user_id_to_follow is None:
        raise QueryError(404, "Usuário não encontrado!")

    if user_id_to_follow == user_id:
        raise QueryError(403, "O usuário não pode seguir a si mesmo!")

    if await is_blocked(conn, user_id_to_follow, user_id):
        raise QueryError(403, "O usuário está tentando seguir alguém que o bloqueou!")
        
    await DB_create_follow(conn, user_id, user_id_to_follow)

    return JSONResponse({"message":"Conta seguida com sucesso!"})


@user_router.delete("/follow/{username}")
async def unfollow(username: str, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Faz o usuário autenticado deixar de seguir outro usuário."""

    user_id_to_unfollow = await DB_read_user_column(conn, "id", username=username)
    
    if user_id_to_unfollow is None:
        raise QueryError(404, "Usuário não encontrado!")
        
    await DB_delete_follow(conn, user_id, user_id_to_unfollow)

    return JSONResponse({"message":"Conta desseguida com sucesso!"})


@user_router.get("/follow")
async def view_follows(conn = Depends(get_conn), user_id = Depends(require_login)):
    """Busca os seguidores e seguidos do usuário autenticado"""

    followings = await DB_read_user_follows(conn, user_id)

    return JSONResponse(followings.model_dump())


@user_router.post("/block/{username}")
async def block_user(username: str, user_id = Depends(require_login), conn = Depends(get_conn)):
    """Faz o usuário autenticado bloquear outro usuário"""

    user_id_to_block = await DB_read_user_column(conn, "id", username=username)

    if user_id_to_block is None:
        raise QueryError(404, "Usuário não encontrado!")

    if user_id_to_block == user_id:
        raise QueryError(403, "O usuário não pode bloquear a si mesmo!")

    async with conn.transaction():
        await DB_create_block(conn, user_id, user_id_to_block)
        await DB_delete_follow(conn, user_id_to_block, user_id)
        await DB_delete_follow(conn, user_id, user_id_to_block)

    return JSONResponse({"message":"Conta bloqueada com sucesso!"})


@user_router.delete("/block/{username}")
async def unblock_user(username: str, user_id = Depends(require_login), conn = Depends(get_conn)):
    """Faz o usuário autenticado desbloquear outro usuário"""

    user_id_to_unblock = await DB_read_user_column(conn, "id", username=username)
        
    if user_id_to_unblock is None:
        raise QueryError(404, "Usuário não encontrado!")

    await DB_delete_block(conn, user_id, user_id_to_unblock)
    return JSONResponse({"message":"Conta desbloqueada com sucesso!"})


@user_router.get("/block")
async def view_blocks(conn = Depends(get_conn), user_id = Depends(require_login)):
    """Busca os usuários bloqueados pelo usuário autenticado"""

    blocks = await DB_read_user_blockeds_full(conn, user_id)
    return JSONResponse(blocks.model_dump())