from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from models.schemas.user import *
from services.security_services import is_user_valid, encrypt_password, encode_token
from services.db_services.user import *
from services.db_services.list import *
from utils import *

user_router = APIRouter(prefix="/user", tags=["user"])

@user_router.post("/")
async def new_user(user: UserIn, conn = Depends(get_conn), key = Depends(get_key)):
    """ Cria uma nova conta de usuário. Ao criar a conta, 2 listas padrão são geradas (Favoritos e Completados)"""

    async with conn.transaction():
        user = await is_user_valid(conn, user)          # Validação do username, email e senha
        user.password = encrypt_password(user.password) # Encriptação da senha  
        new_user_id = await DB_create_user(conn, user)  # Adiciona ao BD
        await first_lists(new_user_id, conn)            # Cria e salva as listas de favoritos e de completados

    # Loga o usuário
    response = JSONResponse({"message":"Conta criada com sucesso!", "id": new_user_id})
    new_access_token = encode_token(new_user_id, 10, key)
    new_refresh_token = encode_token(new_user_id, 1440, key)
    response.set_cookie("access-token", new_access_token, secure=True, httponly=True)
    response.set_cookie("refresh-token", new_refresh_token, secure=True, httponly=True)
    
    return response


async def first_lists(user_id, conn):
    """Cria as listas padrão de todo usuário: Favoritos e Completados"""

    # Cria e salva a lista de favoritos
    favorites_list = ListIn(
        name = "Jogos Favoritos",
        description = "Meus games favoritos",
        is_private = True
    )
    
    favorites_list_id = await DB_create_list(conn, favorites_list, user_id)
    await DB_create_list_save(conn, favorites_list_id, user_id)
        
    # Cria e salva a lista de completados
    finished_list = ListIn(
        name = "Jogos Completados",
        description = "Meus games completados",
        is_private = True
    )

    finished_list_id = await DB_create_list(conn, finished_list, user_id)
    await DB_create_list_save(conn, finished_list_id, user_id)


async def get_user_account_basics(conn, user_id): 
    """Lê os dados completos de uma conta de usuário"""

    out = await DB_read_user_out(conn, user_id)             # Dados da conta do usuário     
    follows = await DB_read_user_follows(conn, user_id)     # Dados de seguidores do usuário
    lists = await DB_read_user_basic_lists(conn, user_id)   # Dados das listas básicas do usuário (completados e favoritos)

    return UserFeed(
        user_id = user_id,
        username=out.username,
        pfp=out.pfp,
        bio=out.bio,
        created_at=out.created_at,
        lists=lists,
        follows=follows
    )


@user_router.get("/")
async def see_my_account(conn = Depends(get_conn), user_id = Depends(require_login)):
    """Retorna os dados completos do usuário autenticado"""

    user_full = await get_user_account_basics(conn, user_id)
    return JSONResponse(user_full.model_dump())


@user_router.put("/")
async def edit_user(user: UserEdit, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Atualiza os dados do usuário autenticado"""

    async with conn.transaction():
        user = await is_user_valid(conn, user, user_id)                 # Validação do username, email e senha
        await DB_update_user(conn, user, user_id)                       # Atualiza o usuário no BD
        user_full = await get_user_account_basics(conn, user_id)       # Busca os dados atualizados do usuário

    return JSONResponse(user_full.model_dump())


@user_router.delete("/")
async def delete_user(conn = Depends(get_conn), user_id = Depends(require_login)):
    """Remove permanentemente a conta do usuário autenticado"""

    await DB_delete_user(conn, user_id)
    return JSONResponse({"message":"Conta deletada com sucesso!"})


@user_router.post("/follow/{user_id}")
async def follow_user(user_id: str, conn = Depends(get_conn), user_id_follower = Depends(require_login)):
    """Faz o usuário autenticado seguir outro usuário"""

    # O user_id providenciado está errado
    if await DB_read_user_column(conn, "username", user_id=user_id) is None:
        raise NotFoundError("Usuário não encontrado!") 

    # O usuário estaá tentando seguir a si mesmo
    if user_id == user_id_follower:
        raise ForbidenError("O usuário não pode seguir a si mesmo!")

    # O usuário está bloqueado por quem ele está tentando seguir
    if await is_blocked(conn, user_id, user_id_follower):
        raise ForbidenError("O usuário está tentando seguir alguém que o bloqueou!")

    # O usuário já segue o outro
    if await already_follows(conn, user_id_follower, user_id):
        # POR WARNING AQ
        return JSONResponse({"message":"Conta seguida com sucesso!"})
        
    await DB_create_follow(conn, user_id_follower, user_id)

    return JSONResponse({"message":"Conta seguida com sucesso!"})


@user_router.delete("/follow/{user_id}")
async def unfollow_user(user_id: str, conn = Depends(get_conn), user_id_follower= Depends(require_login)):
    """Faz o usuário autenticado deixar de seguir outro usuário."""

    # O user_id providenciado está errado
    if await DB_read_user_column(conn, "username", user_id=user_id) is None:
        raise NotFoundError("Usuário não encontrado!") 
        
    await DB_delete_follow(conn, user_id_follower, user_id)

    return JSONResponse({"message":"Conta desseguida com sucesso!"})


@user_router.get("/follow/followers")
async def view_followers(page_query: PageQuery = Depends(), conn = Depends(get_conn), user_id = Depends(require_login), url = Depends(get_current_url)):
    """Busca os seguidores do usuário autenticado"""

    followers_page = await DB_read_user_followers(conn, user_id, page_query)
    followers_page_with_urls = convert_cursors_to_paths(followers_page, url)

    return JSONResponse(followers_page_with_urls.model_dump())


@user_router.get("/follow/followeds")
async def view_followeds(page_query: PageQuery = Depends(), conn = Depends(get_conn), user_id = Depends(require_login), url= Depends(get_current_url)):
    """Busca os seguidos pelo usuário autenticado"""

    followeds_page = await DB_read_user_followeds(conn, user_id, page_query)
    followeds_page_with_urls = convert_cursors_to_paths(followeds_page, url)

    return JSONResponse(followeds_page_with_urls.model_dump())


@user_router.post("/block/{user_id}")
async def block_user(user_id: str, conn = Depends(get_conn), user_id_blocker = Depends(require_login),):
    """Faz o usuário autenticado bloquear outro usuário"""

    # O user_id providenciado está errado
    if await DB_read_user_column(conn, "username", user_id=user_id) is None:
        raise NotFoundError("Usuário não encontrado!") 

    if await is_blocked(conn, user_id_blocker, user_id):
        # POR WARNING AQ
        return JSONResponse({"message":"Conta bloqueada com sucesso!"})

    if user_id == user_id_blocker:
        raise ForbidenError("O usuário não pode bloquear a si mesmo!")

    async with conn.transaction():
        await DB_create_block(conn, user_id_blocker, user_id)
        await DB_delete_follow(conn, user_id_blocker, user_id)
        await DB_delete_follow(conn, user_id, user_id_blocker)

    return JSONResponse({"message":"Conta bloqueada com sucesso!"})


@user_router.delete("/block/{user_id}")
async def unblock_user(user_id: str, conn = Depends(get_conn), user_id_blocker = Depends(require_login)):
    """Faz o usuário autenticado desbloquear outro usuário"""

    # O user_id providenciado está errado
    if await DB_read_user_column(conn, "username", user_id=user_id) is None:
        raise NotFoundError("Usuário não encontrado!") 

    await DB_delete_block(conn, user_id_blocker, user_id)
    return JSONResponse({"message":"Conta desbloqueada com sucesso!"})


@user_router.get("/block")
async def view_blocks(page_query: PageQuery = Depends(), conn = Depends(get_conn), user_id = Depends(require_login), url= Depends(get_current_url)):
    """Busca os usuários bloqueados pelo usuário autenticado"""

    blockeds_page = await DB_read_user_blockeds(conn, user_id, page_query)
    blockeds_page_with_url = convert_cursors_to_paths(blockeds_page, url)

    return JSONResponse(blockeds_page_with_url.model_dump())


@user_router.get("/{user_id}")
async def see_account(user_id: str, conn = Depends(get_conn), user_id_viewer = Depends(optional_login)):
    """Retorna os dados públicos de qualquer usuário pelo user_id"""

    # O user_id providenciado está errado
    if await DB_read_user_column(conn, "username", user_id=user_id) is None:
        raise NotFoundError("Usuário não encontrado!") 

    if (user_id_viewer is not None) and (await is_blocked(conn, user_id, user_id_viewer)):
        raise ForbidenError("Usuário está tentando ver a conta que alguém que o bloqueou!")
        
    user_feed = await get_user_account_basics(conn, user_id)

    return JSONResponse(user_feed.model_dump())
    