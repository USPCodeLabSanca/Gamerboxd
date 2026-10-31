from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from models.schemas.user import *
from services.security_services import is_user_valid, encrypt_password, encode_token, classify_relationship, resolve_user_clearence
from services.db_services.user import *
from services.db_services.list import *
from utils import *

user_router = APIRouter(prefix="/users", tags=["user"])

@user_router.post("")
async def new_user(user: UserIn, conn = Depends(get_conn), key = Depends(get_key)):
    """Cria uma nova conta de usuário. Ao criar a conta, 2 listas padrão são geradas (Favoritos e Completados)"""

    async with conn.transaction():
        user = await is_user_valid(conn, user)          # Validação do username, email e senha
        user.password = encrypt_password(user.password) # Encriptação da senha  
        new_user_id = await DB_create_user(conn, user)  # Adiciona ao BD
        await _first_lists(new_user_id, conn)           # Cria e salva as listas de favoritos e de completados

    # Loga o usuário
    response = JSONResponse({"message":"Conta criada com sucesso!", "user_id": new_user_id})
    new_access_token = encode_token(new_user_id, 10, key)
    new_refresh_token = encode_token(new_user_id, 720, key)
    response.set_cookie("access-token", new_access_token, samesite="strict", secure=True, httponly=True)
    response.set_cookie("refresh-token", new_refresh_token, samesite="strict", secure=True, httponly=True)
    
    return response


async def _first_lists(user_id: str, conn):
    """Cria as listas padrão de todo usuário: Favoritos e Completados"""

    # Cria e salva a lista de favoritos
    favorites_list = ListNew(
        name = "Jogos Favoritos",
        description = "Meus games favoritos",
        privacy = RelationshipStatus.OWNER,
        first_games=[]
    )
    
    favorites_list_id = await DB_create_list(conn, favorites_list, user_id)
    await DB_create_list_save(conn, favorites_list_id, user_id)
        
    # Cria e salva a lista de completados
    finished_list = ListNew(
        name = "Jogos Completados",
        description = "Meus games completados",
        privacy = RelationshipStatus.OWNER,
        first_games=[]
    )

    finished_list_id = await DB_create_list(conn, finished_list, user_id)
    await DB_create_list_save(conn, finished_list_id, user_id)


async def _get_user_account(conn, user_id_viewed: str, rel: int): 
    """Lê os dados completos de uma conta de usuário"""

    out = await DB_read_user_out(conn, user_id_viewed)              # Dados da conta do usuário
    followers, followeds = await DB_read_user_follows(conn, user_id_viewed)      # Dados de seguidores do usuário                 
    lists = await DB_read_user_basic_lists(conn, user_id_viewed)    # Dados das listas básicas do usuário 
    
    return UserDetails(
        user_id=user_id_viewed,
        username=out.username,
        pfp=out.pfp,
        banner=out.banner,
        bio=out.bio,
        created_at=out.created_at,
        lists=lists,
        follower_count=followers,
        following_count=followeds,
        rel=rel
    )


@user_router.put("")
async def edit_user(user: UserEdit, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Atualiza os dados do usuário autenticado"""

    async with conn.transaction():
        user = await is_user_valid(conn, user, user_id)             # Validação do username, email e senha
        await DB_update_user(conn, user, user_id)                   # Atualiza o usuário no BD
        user_full = await _get_user_account(conn, user_id, RelationshipStatus.OWNER)  
    return JSONResponse(user_full.model_dump())


@user_router.delete("")
async def delete_user(conn = Depends(get_conn), user_id = Depends(require_login)):
    """Remove permanentemente a conta do usuário autenticado"""

    await DB_delete_user(conn, user_id)

    response = JSONResponse({"message":"Conta deletada com sucesso!"})
    response.delete_cookie("refresh-token", secure=True, httponly=True, samesite="strict")
    response.delete_cookie("access-token", secure=True, httponly=True, samesite="strict")
    
    return response


@user_router.post("/follow/{user_id}")
async def follow_user(user_id: str, conn = Depends(get_conn), user_id_follower = Depends(require_login)):
    """Faz o usuário autenticado seguir outro usuário"""

    # Verifica se o user_id providenciado está errado
    if await DB_read_user_column(conn, "username", user_id=user_id) is None:
        raise QueryError(404, USER_NOT_FOUND_MSG) 

    prev_relationship = await classify_relationship(conn, user_id_follower, user_id)

    uncleared_relationships = {
        RelationshipStatus.OWNER: (403, "O usuário não pode seguir a si mesmo!"),
    }

    resolve_user_clearence(prev_relationship, uncleared_relationships)

    # O usuário já segue quem ele está tentando seguir (idempotência)
    if prev_relationship in (RelationshipStatus.FOLLOWER, RelationshipStatus.MUTUAL_FOLLOW):
        # POR WARNING AQ
        return JSONResponse({"message":"Conta seguida com sucesso!"})
        
    await DB_create_follow(conn, user_id_follower, user_id)

    return JSONResponse({"message":"Conta seguida com sucesso!"})


@user_router.delete("/follow/{user_id}")
async def unfollow_user(user_id: str, conn = Depends(get_conn), user_id_follower= Depends(require_login)):
    """Faz o usuário autenticado deixar de seguir outro usuário."""

    # O user_id providenciado está errado
    if await DB_read_user_column(conn, "username", user_id=user_id) is None:
        raise QueryError(404, USER_NOT_FOUND_MSG)     
        
    await DB_delete_follow(conn, user_id_follower, user_id)

    return JSONResponse({"message":"Conta desseguida com sucesso!"})


@user_router.get("/follow/followers/{user_id}")
async def view_followers(user_id: str, page_query: PageQuery = Depends(validate_queries(["username", "created_at"], "!created_at")),
    conn = Depends(get_conn), user_id_viewer = Depends(require_login), url = Depends(get_current_url)):
    """Busca os seguidores do usuário SE o visualisador é seguido pelo dono da conta ou se ele é o dono da conta"""

    # Verifica se o user_id providenciado está errado
    if await DB_read_user_column(conn, "username", user_id=user_id) is None:
        raise QueryError(404, USER_NOT_FOUND_MSG) 

    prev_relationship = await classify_relationship(conn, user_id_viewer, user_id)

    uncleared_relationships = {
        RelationshipStatus.FOLLOWER: (403, LACK_OF_USER_PERMISSION_MSG),
        RelationshipStatus.ANY: (403, LACK_OF_USER_PERMISSION_MSG),
    }

    resolve_user_clearence(prev_relationship, uncleared_relationships)
        
    followers_page = await DB_read_user_followers(conn, user_id, page_query)
    followers_page_with_urls = convert_cursors_to_paths(followers_page, url)

    return JSONResponse(followers_page_with_urls.model_dump())


@user_router.get("/follow/following/{user_id}")
async def view_followeds(user_id: str, page_query =Depends(validate_queries(["username", "created_at"], "!created_at")),
    conn = Depends(get_conn), user_id_viewer = Depends(require_login), url= Depends(get_current_url)):
    """Busca os seguidos pelo usuário SE o visualisador é seguido pelo dono da conta ou se ele é o dono da conta"""

    # Verifica se o user_id providenciado está errado
    if await DB_read_user_column(conn, "username", user_id=user_id) is None:
        raise QueryError(404, USER_NOT_FOUND_MSG) 

    prev_relationship = await classify_relationship(conn, user_id_viewer, user_id)

    uncleared_relationships = {
        RelationshipStatus.FOLLOWER: (403, LACK_OF_USER_PERMISSION_MSG),
        RelationshipStatus.ANY: (403, LACK_OF_USER_PERMISSION_MSG),
    }

    resolve_user_clearence(prev_relationship, uncleared_relationships)

    followings_page = await DB_read_user_followings(conn, user_id, page_query)
    followings_page_with_urls = convert_cursors_to_paths(followings_page, url)

    return JSONResponse(followings_page_with_urls.model_dump())


@user_router.post("/block/{user_id}")
async def block_user(user_id: str, conn = Depends(get_conn), user_id_blocker = Depends(require_login)):
    """Faz o usuário autenticado bloquear outro usuário"""

    # O user_id providenciado está errado
    if await DB_read_user_column(conn, "username", user_id=user_id) is None:
        raise QueryError(404, USER_NOT_FOUND_MSG) 

    prev_relationship = await classify_relationship(conn, user_id_blocker, user_id)

    # O usuário está tentando bloquear a si mesmo
    if prev_relationship == RelationshipStatus.OWNER:
        raise QueryError(403, "O usuário não pode bloquear a si mesmo!")

    # O usuário já bloqueou o usuário que está tentando bloquear (idempotência)
    if prev_relationship == RelationshipStatus.BLOCKER:
        return JSONResponse({"message":"Conta bloqueada com sucesso!"})

    async with conn.transaction():
        await DB_create_block(conn, user_id_blocker, user_id)
        await DB_delete_follow(conn, user_id_blocker, user_id)
        await DB_delete_follow(conn, user_id, user_id_blocker)
        await DB_delete_saves_after_block(conn, user_id_blocker, user_id)
        await DB_delete_saves_after_block(conn, user_id, user_id_blocker)

    return JSONResponse({"message":"Conta bloqueada com sucesso!"})


@user_router.delete("/block/{user_id}")
async def unblock_user(user_id: str, conn = Depends(get_conn), user_id_blocker = Depends(require_login)):
    """Faz o usuário autenticado desbloquear outro usuário"""

    # O user_id providenciado está errado
    if await DB_read_user_column(conn, "username", user_id=user_id) is None:
        raise QueryError(404, USER_NOT_FOUND_MSG) 

    await DB_delete_block(conn, user_id_blocker, user_id)
    return JSONResponse({"message":"Conta desbloqueada com sucesso!"})


@user_router.get("/block")
async def view_blocks(page_query = Depends(validate_queries(["username", "created_at"], "!created_at")), 
        conn = Depends(get_conn), user_id = Depends(require_login), url = Depends(get_current_url)):
    """Busca os usuários bloqueados pelo usuário autenticado"""

    blockeds_page = await DB_read_user_blockeds(conn, user_id, page_query)
    blockeds_page_with_url = convert_cursors_to_paths(blockeds_page, url)

    return JSONResponse(blockeds_page_with_url.model_dump())


@user_router.get("/{user_id}")
async def see_account(user_id: str, conn = Depends(get_conn), user_id_viewer = Depends(require_login)):
    """Retorna os dados públicos de um usuário pelo user_id"""

    # O user_id providenciado está errado
    if await DB_read_user_column(conn, "username", user_id=user_id) is None:
        raise QueryError(404, "Usuário não encontrado!") 

    prev_relationship = await classify_relationship(conn, user_id_viewer, user_id)

    resolve_user_clearence(prev_relationship)
        
    user_feed = await _get_user_account(conn, user_id, prev_relationship)

    return JSONResponse(user_feed.model_dump())
    