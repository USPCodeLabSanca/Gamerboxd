from fastapi import Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from models.schemas import *
from services.security_services import *
from services.db_services import *
from utils.dependencies import get_conn, require_login, require_key


user_router = InferringRouter(prefix="/user", tags=["user"])

@cbv(user_router)
class NewUserController:

    @user_router.post("/")
    async def new_user(self, user: UserIn, conn = Depends(get_conn), key = Depends(require_key)):

        # Validação do username, email e senha
        try:
            user.username = await is_username_valid(user.username, conn)
            user.email =  await is_email_valid(user.email, conn)
            user.password = is_password_valid(user.password)      
            user.password = encrypt_password(user.password)

        except Exception as e:
            raise HTTPException(500, detail = str(e))

        account_creation_result = await DB_create_user(conn, user)

        if not account_creation_result.success:
            raise HTTPException(500, str(account_creation_result.error))
        
        user_id = account_creation_result.obj

        # Cria e salva as listas de favoritos e de completados
        try:
            await self.create_and_save_lists(user_id, conn)

        except Exception as e:
            raise HTTPException(500, detail = str(e))
        
        #Adiciona as tags do usuário (ainda não existe a tabela de tags com os nomes)
        #for tag in user.tags.tags:
        #    user_tag_creation_result = await DB_create_user_tags(conn, user_id, tag)
        #    if not user_tag_creation_result.success:
        #        return JSONResponse({"message": str(user_tag_creation_result.error)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        new_access_token = encode_token(account_creation_result.obj, 10, key)
        new_refresh_token = encode_token(account_creation_result.obj, 1440, key)

        response = JSONResponse({"message":account_creation_result.message}, status.HTTP_202_ACCEPTED)
        response.set_cookie("access-token", new_access_token, secure=True, httponly=True)
        response.set_cookie("refresh-token", new_refresh_token, secure=True, httponly=True)
        
        return response
      
    @staticmethod
    async def create_and_save_lists(user_id, conn):
        async with conn.transaction():

            try:
                # Cria a lista de favoritos
                favorites_list = List(
                    creator = user_id,
                    name = "Favoritos",
                    description = "Meus games favoritos",
                    is_private = True
                )
                
                favorites_list_creation_result = await DB_create_list(conn, favorites_list)
                if not favorites_list_creation_result.success:
                    raise favorites_list_creation_result.error
                    
                # Cria a lista de completados
                finished_list = List(
                    creator = user_id,
                    name = "Completados",
                    description = "Meus games completados",
                    is_private = True
                )

                finished_list_creation_result = await DB_create_list(conn, finished_list)
                if not finished_list_creation_result.success:
                    raise finished_list_creation_result.error
                
                # Salva a lista de favoritos
                favorites_list_id = favorites_list_creation_result.obj
                favorites_list_saving_result = await DB_create_saved_list(conn, favorites_list_id, user_id)
                if not favorites_list_saving_result.success:
                    raise favorites_list_saving_result.error
                
                # Salva a lista de completados
                finished_list_id = finished_list_creation_result.obj
                finished_list_saving_result = await DB_create_saved_list(conn, finished_list_id, user_id)
                if not finished_list_saving_result.success:
                    raise finished_list_saving_result.error
            
            except Exception as e:
                raise HTTPException(500, detail=str(e))
        

@cbv(user_router)
class SeeMyAccountController:

    @staticmethod
    async def get_full(conn, user_id):        
        
        out = await DB_read_user_out(conn, user_id=user_id)       
        follows = await DB_read_user_follows(conn, user_id=user_id)
        tags = await DB_read_user_tags(conn, user_id=user_id)
        lists= await DB_read_user_lists(conn, user_id=user_id)
        
        for result in (out, tags, lists, follows):
            if not result.success:
                raise result.error

        user_full = UserFull(
            username=out.obj.username,
            pfp=out.obj.pfp,
            email=out.obj.email,
            bio=out.obj.bio,
            created_at=out.obj.created_at,
            tags=tags.obj,
            lists=lists.obj,
            follows=follows.obj
        )

        return user_full

    @user_router.get("/")
    async def see_my_account(self, conn = Depends(get_conn), user_id = Depends(require_login)):
        try:
            user_full = await self.get_full(conn, user_id)

        except Exception as e:
            raise HTTPException(500, detail=str(e))

        return JSONResponse(user_full.model_dump(), status.HTTP_200_OK)


@cbv(user_router)
class SeeAccountController(SeeMyAccountController):
    
    @user_router.get("/view/{username}")
    async def see_account(self, username: str, conn = Depends(get_conn)):

        user_id_result = await DB_read_user_column(conn, "user_id", username=username)
        if not user_id_result.success:
            raise HTTPException(500, detail=str(user_id_result.error))            
        
        user_id = user_id_result.obj
        if not user_id:
            raise HTTPException(500, detail="Não encontramos o usuário")

        try:
            user_full = await self.get_full(conn, user_id)

        except Exception as e:
            raise HTTPException(500, detail=str(e))

        return JSONResponse(user_full.model_dump(), status.HTTP_200_OK)


@cbv(user_router)
class FollowController:
    
    @user_router.get("/follow/{username}")
    async def follow(self, username: str, conn = Depends(get_conn), user_id = Depends(require_login)):

        user_id_to_follow_result = await DB_read_user_column(conn, "user_id", username=username)
        if not user_id_to_follow_result.success:
            raise HTTPException(500, detail=str(user_id_to_follow_result.error))
            

        user_id_to_follow = user_id_to_follow_result.obj
        if not user_id_to_follow:
            raise HTTPException(500, detail="Não encontramos o usuário a ser seguido!")
            
        try:
            follow_result = await DB_create_follow(conn, user_id, user_id_to_follow)
            if not follow_result.success:
                raise HTTPException(500, detail=str(follow_result.error))

        except Exception as e:
            raise HTTPException(500, detail=str(e))

        return JSONResponse({"message":follow_result.message}, status.HTTP_202_ACCEPTED)


@cbv(user_router)
class UnfollowController:
    
    @user_router.get("/unfollow/{username}")
    async def unfollow(self, username: str, conn = Depends(get_conn), user_id = Depends(require_login)):

        user_id_to_unfollow_result = await DB_read_user_column(conn, "user_id", username=username)
        if not user_id_to_unfollow_result.success:
            raise HTTPException(500, detail=str(user_id_to_unfollow_result.error))
            

        user_id_to_unfollow = user_id_to_unfollow_result.obj
        if not user_id_to_unfollow:
            raise HTTPException(500, detail="Não encontramos o usuário a ser desseguido!")
            
        try:
            unfollow_result = await DB_delete_follow(conn, user_id, user_id_to_unfollow)
            if not unfollow_result.success:
                raise HTTPException(500, detail=str(unfollow_result.error))

        except Exception as e:
            raise HTTPException(500, detail=str(e))

        return JSONResponse({"message":unfollow_result.message}, status.HTTP_202_ACCEPTED)