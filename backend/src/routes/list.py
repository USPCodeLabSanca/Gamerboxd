from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from models.schemas.list import *
from services.security_services import is_list_valid, is_blocked
from services.db_services import *
from utils import *

list_router = APIRouter(prefix="/list", tags=["list"])


@list_router.post("/")
async def new_list(new_list: ListIn, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Cria uma nova lista para o usuário autenticado. Ao ser criada, a lista é automaticamente salva para o criador"""

    validated_list = await is_list_valid(conn, user_id, new_list)

    # Cria e salva para o usuário a lista
    async with conn.transaction():
        new_list_id = await DB_create_list(conn, validated_list, user_id)
        await DB_create_list_save(conn, new_list_id, user_id)

    return JSONResponse({"message":"Lista criada com sucesso!", "id": new_list_id})
    

@list_router.delete("/{list_id}")
async def delete_list(list_id: str, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Remove uma lista do usuário autenticado"""

    list_creator_id = await DB_read_list_creator(conn, list_id)

    if list_creator_id is None:
        raise NotFoundError(LIST_NOT_FOUND_MSG)

    # Usuário não é o dono da lista
    if list_creator_id != user_id:
        raise ForbidenError(LACK_OF_LIST_OWNERSHIP_MSG)

    list_name = await DB_read_list_name(conn, list_id)

    if list_name in ("Jogos Completados", "Jogos Favoritos"):
        raise ForbidenError("Não é possível deletar essa lista!")

    await DB_delete_list(conn, list_id)

    return JSONResponse({"message":"Lista deletada com sucesso!"})


@list_router.put("/{list_id}")
async def edit_list(list_id: str, new_list: ListIn, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Atualiza os dados de uma lista do usuário autenticado e retorna os seus dados"""

    list_creator_id = await DB_read_list_creator(conn, list_id)

    if list_creator_id is None:
        raise NotFoundError(LIST_NOT_FOUND_MSG)

    if list_creator_id != user_id:
        raise ForbidenError(LACK_OF_LIST_OWNERSHIP_MSG)

    current_list_name = await DB_read_list_name(conn, list_id)
    if current_list_name in ("Jogos Completados", "Jogos Favoritos") and new_list.name != current_list_name:
        raise ForbidenError("Não é possível alterar o nome dessa lista!")

    list_for_insertion = await is_list_valid(conn, user_id, new_list, list_id)

    # Se a privacidade mudou de público para privado, é necessário apagar a lista de todos as bibliotecas que a salvaram
    current_list_privacy = await DB_read_list_privacy(conn, list_id)
    if list_for_insertion.is_private == True and current_list_privacy == False:
        await DB_delete_list_saves_after_privacy_change(conn, list_id, user_id)

    await DB_update_list(conn, list_id, list_for_insertion)
    list_data = await DB_read_list_data(conn, list_id)
    
    return JSONResponse(list_data.model_dump())


@list_router.get("/saved")
async def view_saved_lists(page_query: PageQuery = Depends(), conn = Depends(get_conn), user_id = Depends(require_login), path = Depends(get_current_url)):
    """Busca as listas salvas pelo usuário"""

    saved_lists_page = await DB_read_user_saved_lists(conn, user_id, page_query)
    saved_lists_page_with_urls = convert_cursors_to_paths(saved_lists_page, path)

    return JSONResponse(saved_lists_page_with_urls.model_dump())


@list_router.get("/created")
async def view_created_lists(page_query: PageQuery = Depends(), conn = Depends(get_conn), user_id = Depends(require_login), path = Depends(get_current_url)):
    """Busca as listas criadas pelo usuário"""

    created_lists_page = await DB_read_user_created_lists(conn, user_id, page_query)
    created_lists_page_with_urls = convert_cursors_to_paths(created_lists_page, path)

    return JSONResponse(created_lists_page_with_urls.model_dump())


@list_router.get("/{list_id}")
async def see_list(list_id: str, conn = Depends(get_conn), user_id = Depends(optional_login)):
    """Retorna os dados completos de uma lista"""

    list_creator_id = await DB_read_list_creator(conn, list_id)

    if list_creator_id is None:
        raise NotFoundError(LIST_NOT_FOUND_MSG)

    list_is_private = await DB_read_list_privacy(conn, list_id)

    if user_id is not None:
        # Usuário está bloqueado pelo autor da lista
        if await is_blocked(conn, list_creator_id, user_id):
            raise ForbidenError(BLOCKED_BY_LIST_OWNER)

        # Usuário está tentando ver lista privada que não o pertence
        if (list_is_private) and (user_id != list_creator_id):
            raise ForbidenError(PRIVATE_LIST_MSG)

    elif list_is_private:
        raise ForbidenError(PRIVATE_LIST_MSG)

    list_data = await DB_read_list_data(conn, list_id)

    return JSONResponse(list_data.model_dump())


@list_router.post("/save/{list_id}")
async def save_list(list_id: str, conn = Depends(get_conn), user_id = Depends(require_login)):  
    """Salva a lista pública de outro usuário na biblioteca do autenticado"""

    list_creator_id = await DB_read_list_creator(conn, list_id)

    if list_creator_id is None:
        raise NotFoundError(LIST_NOT_FOUND_MSG)

    # Usuário tentando salvar sua própria lista
    if list_creator_id == user_id:
        raise ForbidenError("Usuário está tentando salvar sua própria lista!")
    
    # Usuário está bloqueado pelo criador da lista
    if await is_blocked(conn, list_creator_id, user_id):
        raise ForbidenError(BLOCKED_BY_LIST_OWNER)

    # Usuário está tentando salvar lista privada
    if await DB_read_list_privacy(conn, list_id):
        raise ForbidenError(PRIVATE_LIST_MSG)
        
    await DB_create_list_save(conn, list_id, user_id)
    
    return JSONResponse({"message": "Lista salva com sucesso!"})


@list_router.delete("/save/{list_id}")
async def unsave_list(list_id: str, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Remove uma lista previamente salva da biblioteca do usuário autenticado"""

    list_creator_id = await DB_read_list_creator(conn, list_id)

    if list_creator_id is None:
        raise NotFoundError(LIST_NOT_FOUND_MSG)

    if list_creator_id == user_id:
        raise ForbidenError("Não é possível dessalvar sua própria lista, apenas deletá-la!")
    
    await DB_delete_list_save(conn, list_id, user_id)
    
    return JSONResponse({"message": "Lista dessalvada com sucesso"})


@list_router.post("/game/{list_id}/{game_id}")
async def add_to_list(list_id: str, game_id: int, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Adiciona um jogo a uma lista do usuário autenticado"""

    list_creator_id = await DB_read_list_creator(conn, list_id)

    if list_creator_id is None:
        raise NotFoundError(LIST_NOT_FOUND_MSG)

    if list_creator_id != user_id:
        raise ForbidenError(LACK_OF_LIST_OWNERSHIP_MSG)

    await DB_create_list_game(conn, list_id, game_id)

    return JSONResponse({"message": "Jogo adicionado à lista com sucesso"})


@list_router.delete("/game/{list_id}/{game_id}")
async def rem_from_list(list_id: str, game_id: int, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Remove um jogo de uma lista do usuário autenticado"""

    list_creator_id = await DB_read_list_creator(conn, list_id)

    if list_creator_id is None:
        raise NotFoundError(LIST_NOT_FOUND_MSG)

    if user_id != list_creator_id:
        raise ForbidenError(LACK_OF_LIST_OWNERSHIP_MSG)

    await DB_delete_list_game(conn, list_id, game_id)

    return JSONResponse({"message": "Jogo removido da lista com sucesso"})


@list_router.get("/game/{list_id}")
async def view_list_games(list_id: str, page_query: PageQuery = Depends(), conn = Depends(get_conn), user_id = Depends(optional_login), path = Depends(get_current_url)):
    """Busca os games que pertencem a uma lista do usuário"""

    list_creator_id = await DB_read_list_creator(conn, list_id)

    if list_creator_id is None:
        raise NotFoundError(LIST_NOT_FOUND_MSG)

    list_is_private = await DB_read_list_privacy(conn, list_id)

    if user_id is not None:
        # Usuário está bloqueado pelo autor da lista
        if await is_blocked(conn, list_creator_id, user_id):
            raise ForbidenError(BLOCKED_BY_LIST_OWNER)

        # Usuário está tentando ver lista privada que não o pertence
        if (list_is_private) and (user_id != list_creator_id):
            raise ForbidenError(PRIVATE_LIST_MSG)

    elif list_is_private:
        raise ForbidenError(PRIVATE_LIST_MSG)

    list_games_page = await DB_read_list_games(conn, list_id, page_query)
    list_games_page_with_urls = convert_cursors_to_paths(list_games_page, path)

    return JSONResponse(list_games_page_with_urls.model_dump())
