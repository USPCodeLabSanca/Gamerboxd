from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from models.schemas.list import *
from services.security_services import is_list_insertion_valid, is_list_update_valid, classify_relationship, resolve_list_clearence
from services.db_services.list import *
from services.db_services.user import DB_read_user_column
from utils import *

list_router = APIRouter(prefix="/lists", tags=["list"])


@list_router.post("")
async def new_list(new_list: ListNew, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Cria uma nova lista para o usuário autenticado. Ao ser criada, a lista é automaticamente salva para o criador"""

    validated_list = await is_list_insertion_valid(conn, user_id, new_list)

    # Cria e salva para o usuário a lista
    async with conn.transaction():
        new_list_id = await DB_create_list(conn, validated_list, user_id)
        await DB_create_list_save(conn, new_list_id, user_id)

        for g in new_list.first_games:
            await DB_create_list_game(conn, new_list_id, g)

    return JSONResponse({"message":"Lista criada com sucesso!", "list_id": new_list_id})
    

@list_router.delete("/{list_id}")
async def delete_list(list_id: str, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Remove uma lista do usuário autenticado"""

    list_creator_id = await DB_read_list_creator(conn, list_id)

    if list_creator_id is None:
        raise QueryError(404, LIST_NOT_FOUND_MSG)

    # Usuário não é o dono da lista
    if list_creator_id != user_id:
        raise QueryError(403, LACK_OF_LIST_OWNERSHIP_MSG)

    list_name = await DB_read_list_name(conn, list_id)

    if list_name in ("Jogos Completados", "Jogos Favoritos"):
        raise QueryError(435, "Não é possível deletar essa lista!")

    await DB_delete_list(conn, list_id)

    return JSONResponse({"message":"Lista deletada com sucesso!"})


@list_router.put("/{list_id}")
async def edit_list(list_id: str, new_list: List, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Atualiza os dados de uma lista do usuário autenticado e retorna os seus dados"""

    list_creator_id = await DB_read_list_creator(conn, list_id)

    if list_creator_id is None:
        raise QueryError(404, LIST_NOT_FOUND_MSG)

    if list_creator_id != user_id:
        raise QueryError(403, LACK_OF_LIST_OWNERSHIP_MSG)

    list_to_edit = await is_list_update_valid(conn, user_id, new_list, list_id)

    # Se a privacidade mudou de público para privado, é necessário apagar a lista de todos as bibliotecas que a salvaram
    current_list_privacy = await DB_read_list_privacy(conn, list_id)
    if list_to_edit.privacy >= current_list_privacy:
        await DB_delete_list_saves_after_privacy_change(conn, list_id, user_id)

    await DB_update_list(conn, list_id, list_to_edit)
    list_data = await DB_read_list_data(conn, list_id)
    list_data.rel = RelationshipStatus.OWNER
    
    return JSONResponse(list_data.model_dump())


@list_router.get("/created/{user_id}")
async def view_created_lists(user_id: str, page_query = Depends(validate_queries(["name", "created_at", "updated_at"], "!updated_at")),
    conn = Depends(get_conn), user_id_viewer = Depends(optional_login), path = Depends(get_current_url)):
    """Busca as listas criadas pelo usuário"""

    # Verifica se o user_id providenciado está errado
    if await DB_read_user_column(conn, "username", user_id=user_id) is None:
        raise QueryError(404, USER_NOT_FOUND_MSG) 

    # Verifica qual a relação do usuário visualizador com o usuário criador das listas
    prev_relationship = await classify_relationship(conn, user_id_viewer, user_id)
    resolve_list_clearence(prev_relationship, None)

    created_lists_page = await DB_read_user_created_lists(conn, user_id, prev_relationship, page_query)

    # Verifica qual o relacionamento do usuário que está vendo com cada lista
    for cl in created_lists_page.content:
        if cl.creator.user_id == user_id_viewer:
            cl.rel = RelationshipStatus.OWNER
        else:
            has_saved = await DB_read_user_has_saved_list(conn, cl.list_id, user_id_viewer)
            cl.rel = RelationshipStatus.SAVED if has_saved else RelationshipStatus.ANY

    created_lists_page_with_urls = convert_cursors_to_paths(created_lists_page, path)

    return JSONResponse(created_lists_page_with_urls.model_dump())


@list_router.post("/save/{list_id}")
async def save_list(list_id: str, conn = Depends(get_conn), user_id = Depends(require_login)):  
    """Salva a lista pública de outro usuário na biblioteca do autenticado"""

    list_creator_id = await DB_read_list_creator(conn, list_id)

    if list_creator_id is None:
        raise QueryError(404, LIST_NOT_FOUND_MSG)

    list_privacy = await DB_read_list_privacy(conn, list_id)
    prev_relationship = await classify_relationship(conn, user_id, list_creator_id)

    uncleared_relationships = {
        RelationshipStatus.OWNER: (403, "Usuário está tentando salvar sua própria lista!")
    } 

    resolve_list_clearence(prev_relationship, list_privacy, uncleared_relationships)
        
    await DB_create_list_save(conn, list_id, user_id)
    
    return JSONResponse({"message": "Lista salva com sucesso!"})


@list_router.delete("/save/{list_id}")
async def unsave_list(list_id: str, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Remove uma lista previamente salva da biblioteca do usuário autenticado"""

    list_creator_id = await DB_read_list_creator(conn, list_id)

    if list_creator_id is None:
        raise QueryError(404, LIST_NOT_FOUND_MSG)

    if list_creator_id == user_id:
        raise QueryError(403, "O usuário está tentando dessalvar sua própria lista!")
    
    await DB_delete_list_save(conn, list_id, user_id)
    
    return JSONResponse({"message": "Lista dessalva com sucesso!"})


@list_router.get("/save")
async def view_saved_lists(page_query = Depends(validate_queries(["name", "created_at"], "!created_at")),
    conn = Depends(get_conn), user_id = Depends(require_login), path = Depends(get_current_url)):
    """Busca as listas salvas pelo usuário"""

    saved_lists_page = await DB_read_user_saved_lists(conn, user_id, page_query)
    saved_lists_page_with_urls = convert_cursors_to_paths(saved_lists_page, path)

    return JSONResponse(saved_lists_page_with_urls.model_dump())


@list_router.post("/game/{list_id}/{game_id}")
async def add_to_list(list_id: str, game_id: int, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Adiciona um jogo a uma lista do usuário autenticado"""

    list_creator_id = await DB_read_list_creator(conn, list_id)

    if list_creator_id is None:
        raise QueryError(404, LIST_NOT_FOUND_MSG)

    if list_creator_id != user_id:
        raise QueryError(403, LACK_OF_LIST_OWNERSHIP_MSG)

    list_name = await DB_read_list_name(conn, list_id)

    if list_name in ("Jogos Favoritos", "Jogos Completados"):
        raise QueryError(400, "Não é possível adicionar games a esta lista sem escrever uma review!")

    if await DB_read_game_in_list(conn, list_id, game_id):
        raise QueryError(409, "Esse game já está na lista!")

    await DB_create_list_game(conn, list_id, game_id)

    return JSONResponse({"message": "Game adicionado à lista com sucesso!"})


@list_router.delete("/game/{list_id}/{game_id}")
async def rem_from_list(list_id: str, game_id: int, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Remove um jogo de uma lista do usuário autenticado"""

    list_creator_id = await DB_read_list_creator(conn, list_id)

    if list_creator_id is None:
        raise QueryError(404, LIST_NOT_FOUND_MSG)

    if user_id != list_creator_id:
        raise QueryError(403, LACK_OF_LIST_OWNERSHIP_MSG)

    list_name = await DB_read_list_name(conn, list_id)

    if list_name in ("Jogos Favoritos", "Jogos Completados"):
        raise QueryError(435, "Não é possível remover games desta lista sem deletar sua review!")

    await DB_delete_list_game(conn, list_id, game_id)

    return JSONResponse({"message": "Game removido da lista com sucesso!"})


@list_router.get("/game/{list_id}")
async def view_list_games(list_id: str, page_query = Depends(validate_queries(["name", "created_at"], "created_at")),
    conn = Depends(get_conn), user_id = Depends(optional_login), path = Depends(get_current_url)):
    """Busca os games que pertencem a uma lista do usuário"""

    list_creator_id = await DB_read_list_creator(conn, list_id)

    if list_creator_id is None:
        raise QueryError(404, LIST_NOT_FOUND_MSG)

    list_privacy = await DB_read_list_privacy(conn, list_id)
    prev_relationship = await classify_relationship(conn, user_id, list_creator_id)

    resolve_list_clearence(prev_relationship, list_privacy)

    list_games_page = await DB_read_list_games(conn, list_id, page_query)
    list_games_page_with_urls = convert_cursors_to_paths(list_games_page, path)

    return JSONResponse(list_games_page_with_urls.model_dump())


@list_router.get("/{list_id}")
async def view_list_data(list_id: str, conn = Depends(get_conn), user_id = Depends(optional_login)):
    """Busca os dados completos de uma lista"""

    list_creator_id = await DB_read_list_creator(conn, list_id)

    if list_creator_id is None:
        raise QueryError(404, LIST_NOT_FOUND_MSG)

    list_privacy = await DB_read_list_privacy(conn, list_id)
    prev_relationship = await classify_relationship(conn, user_id, list_creator_id)

    resolve_list_clearence(prev_relationship, list_privacy)

    list_data = await DB_read_list_data(conn, list_id)
    if prev_relationship == RelationshipStatus.OWNER:
        list_data.rel = RelationshipStatus.OWNER

    else:
        has_saved = await DB_read_user_has_saved_list(conn, list_id, user_id)
        list_data.rel = RelationshipStatus.SAVED if has_saved else RelationshipStatus.ANY

    return JSONResponse(list_data.model_dump())