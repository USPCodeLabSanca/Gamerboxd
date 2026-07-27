from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from models.schemas.list import *
from services.security_services import is_list_valid
from services.db_services import *
from utils.dependencies import get_conn, require_login
from utils.utils import QueryError

list_router = APIRouter(prefix="/list", tags=["list"])


@list_router.post("/")
async def new_list(new_list: ListIn, conn = Depends(get_conn), user_id = Depends(require_login)):
    validated_list = await is_list_valid(conn, user_id, new_list)
    new_list_id = await DB_create_list(conn, validated_list)
    await DB_create_list_save(conn, new_list_id, user_id)

    return JSONResponse({"message":"Lista criada com sucesso"})
    

@list_router.delete("/{list_name}")
async def delete_list(list_name: str, conn = Depends(get_conn), user_id = Depends(require_login)):
    await DB_delete_list(conn, list_name, user_id)

    return JSONResponse({"message":"Lista deletada com sucesso"})


@list_router.get("/{list_creator}/{list_name}")
async def see_list(list_creator: str, list_name: str, conn = Depends(get_conn)):
    list_creator_id = await DB_read_user_column(conn, "user_id", username=list_creator.strip())
    list_id = await DB_read_user_list_id(conn, list_creator_id, list_name.strip(), only_public = True)

    if list_id is None:
        raise QueryError(404, "Lista não encontrada!")

    list_full = await DB_read_list_full(conn, list_id)

    return JSONResponse(list_full.model_dump())


@list_router.get("/{list_name}")
async def see_my_list(list_name: str, conn = Depends(get_conn), user_id = Depends(require_login)):
    list_id = await DB_read_user_list_id(conn, user_id, list_name.strip(), only_public = False)

    if list_id is None:
        raise QueryError(404, "Lista não encontrada!")

    list_full = await DB_read_list_full(conn, list_id)

    return JSONResponse(list_full.model_dump())


@list_router.put("/{old_list_name}")
async def edit_list(old_list_name: str, new_list: ListIn, conn = Depends(get_conn), user_id = Depends(require_login)):
    list_for_insertion = await is_list_valid(conn, user_id, new_list)
    list_update = await DB_update_list(conn, list_for_insertion, old_list_name, user_id)
    
    return JSONResponse(list_update.model_dump())


@list_router.post("/save/{list_creator}/{list_name}")
async def save_list(list_creator: str, list_name: str, conn = Depends(get_conn), user_id = Depends(require_login)):  
    list_creator_id = await DB_read_user_column(conn, "user_id", username=list_creator.strip())

    if list_creator_id is None:
        raise QueryError(404, "Usuário não encontrado!")
    
    list_id = await DB_read_user_list_id(conn, list_creator_id, list_name.strip(), only_public = True)

    if list_id is None:
        raise QueryError(404, "Lista não encontrada!")
    
    await DB_create_list_save(conn, list_id, user_id)
    
    return JSONResponse({"message": "Lista salva com sucesso"})


@list_router.post("/unsave/{list_creator}/{list_name}")
async def unsave_list(list_creator: str, list_name: str, conn = Depends(get_conn), user_id = Depends(require_login)):
    list_creator_id = await DB_read_user_column(conn, "user_id", username=list_creator.strip())

    if list_creator_id is None:
        raise QueryError(404, "Usuário não encontrado!")
    
    list_id = await DB_read_user_list_id(conn, list_creator_id, list_name.strip(), only_public = True)

    if list_id is None:
        raise QueryError(404, "Lista não encontrada!")
    
    await DB_delete_list_save(conn, list_id, user_id)
    
    return JSONResponse({"message": "Lista dessalvada com sucesso"})


@list_router.post("/add/{list_name}/{game_id}")
async def save_to_list(list_name: str, game_id: int, conn = Depends(get_conn), user_id = Depends(require_login)):
    list_id = await DB_read_user_list_id(conn, user_id, list_name, only_public = False)

    if list_id is None:
        raise QueryError(404, "Lista não encontrada!")

    await DB_create_list_game(conn, list_id, game_id)

    return JSONResponse({"message": "Jogo adicionado à lista com sucesso"})


@list_router.post("/rem/{list_name}/{game_id}")
async def rem_from_list(list_name: str, game_id: int, conn = Depends(get_conn), user_id = Depends(require_login)):
    list_id = await DB_read_user_list_id(conn, user_id, list_name, only_public = False)

    if list_id is None:
        raise QueryError(404, "Lista não encontrada!")

    await DB_delete_list_game(conn, list_id, game_id)

    return JSONResponse({"message": "Jogo removido da lista com sucesso"})
            
