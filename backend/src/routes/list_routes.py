from fastapi import Depends, status
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from models.schemas import *
from services.security_services import *
from services.db_services import *
from utils.dependencies import get_conn, require_login

list_router = InferringRouter(prefix="/list", tags=["list"])

@cbv(list_router)
class NewListController:

    @list_router.post("/")
    async def new_list(self, new_list: ListIn, conn = Depends(get_conn), user_id = Depends(require_login)):

        # Validação dos detalhes da lista
        try:
            list_for_insertion = await is_list_valid(conn, user_id, new_list)

        except HTTPException as he:
            raise he
        
        except Exception as e:
            raise HTTPException(500, detail=str(e))

        list_creation_result = await DB_create_list(conn, list_for_insertion)

        if not list_creation_result.success or not list_creation_result.obj:
            raise HTTPException(500, str(list_creation_result.error))
        
        new_list_id = list_creation_result.obj

        saving_new_list_result = await DB_create_saved_list(conn, new_list_id, user_id)

        if not saving_new_list_result.success:
            raise HTTPException(500, str(saving_new_list_result.error))
        
        return JSONResponse({"message":saving_new_list_result.message}, status.HTTP_202_ACCEPTED)
        

@cbv(list_router)
class DeleteListController:

    @list_router.delete("/{list_name}")
    async def delete_list(self, list_name: str, conn = Depends(get_conn), user_id = Depends(require_login)):
        
        list_deletion_result = await DB_delete_list(conn, list_name, user_id)

        if not list_deletion_result.success:
            raise HTTPException(500, str(list_deletion_result.error))
                
        return JSONResponse({"message":list_deletion_result.message}, status.HTTP_202_ACCEPTED)
    

@cbv(list_router)
class EditListController:

    @list_router.put("/{old_list_name}")
    async def edit_list(self, old_list_name: str, new_list: ListIn, conn = Depends(get_conn), user_id = Depends(require_login)):

        # Validação dos detalhes da lista
        try:
            list_for_insertion = await is_list_valid(conn, user_id, new_list)

        except HTTPException as he:
            raise he
        
        except Exception as e:
            raise HTTPException(500, detail=str(e))
        
        list_update_result = await DB_update_list(conn, list_for_insertion, old_list_name, user_id)

        if not list_update_result.success or not list_update_result.obj:
            raise HTTPException(500, str(list_update_result.error))
        
        list_update = list_update_result.obj
        
        return JSONResponse(list_update.model_dump(), status.HTTP_202_ACCEPTED)

@cbv(list_router)
class SaveListController:

    @list_router.post("/save/{list_creator}/{list_name}")
    async def save_list(self, list_creator: str, list_name: str, conn = Depends(get_conn), user_id = Depends(require_login)):
        
        list_creator_id_result = await DB_read_user_column(conn, "user_id", username=list_creator.strip())

        if not list_creator_id_result.success:
            raise HTTPException(500, detail=str(list_creator_id_result.error))
        
        if list_creator_id_result.obj is None:
            raise HTTPException(400, detail="Erro ao identificar o dono da lista")
        
        list_creator_id = list_creator_id_result.obj

        list_id_result = await DB_read_user_list_id(conn, list_creator_id, list_name.strip(), only_public = True)

        if not list_id_result.success:
            raise HTTPException(500, detail=str(list_id_result.error))
        
        if list_id_result.obj is None:
            raise HTTPException(400, detail="Erro ao localizar a lista")
        
        list_id = list_id_result.obj

        list_saving_result = await DB_create_list_save(conn, list_id, user_id)

        if not list_saving_result.success:
            raise HTTPException(500, detail=str(list_saving_result.error))
        
        return JSONResponse({"message": "Lista salva com sucesso"}, status_code=status.HTTP_201_CREATED)


@cbv(list_router)
class UnSaveListController:

    @list_router.post("/unsave/{list_creator}/{list_name}")
    async def unsave_list(self, list_creator: str, list_name: str, conn = Depends(get_conn), user_id = Depends(require_login)):
        
        list_creator_id_result = await DB_read_user_column(conn, "user_id", username=list_creator.strip())

        if not list_creator_id_result.success:
            raise HTTPException(500, detail=str(list_creator_id_result.error))
        
        if list_creator_id_result.obj is None:
            raise HTTPException(400, detail="Erro ao identificar o dono da lista")
        
        list_creator_id = list_creator_id_result.obj

        list_id_result = await DB_read_user_list_id(conn, list_creator_id, list_name.strip(), only_public = True)

        if not list_id_result.success:
            raise HTTPException(500, detail=str(list_id_result.error))
        
        if list_id_result.obj is None:
            raise HTTPException(400, detail="Erro ao localizar a lista")
        
        list_id = list_id_result.obj

        list_unsaving_result = await DB_delete_list_save(conn, list_id, user_id)

        if not list_unsaving_result.success:
            raise HTTPException(500, detail=str(list_unsaving_result.error))
        
        return JSONResponse({"message": "Lista esquecida com sucesso"}, status_code=status.HTTP_201_CREATED)


