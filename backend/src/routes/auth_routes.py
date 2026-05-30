from fastapi import Depends, status, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from models.schemas import *
from services.security_services import *
from services.db_services import *
from utils.dependencies import get_conn, get_key


auth_router = InferringRouter(prefix="/auth", tags=["auth"])

@cbv(auth_router)
class LoginController:
    @auth_router.post("/login/")
    async def login(self, user: UserAuth, conn = Depends(get_conn), key = Depends(get_key)):

        user_id_result = await DB_read_user_column(conn, "user_id", username=user.email_or_username, email=user.email_or_username)

        if not user_id_result.success:
            raise HTTPException(500, detail= str(user_id_result.error))
        
        user_id = user_id_result.obj

        if not user_id:
            raise HTTPException(400, detail= "Essa conta não existe")

        password_result = await DB_read_user_column(conn, "password", user_id=user_id)

        if not password_result.success:
            raise HTTPException(500, detail= str(password_result.error))

        if not passwords_match(password_result.obj, user.password):
            raise HTTPException(400, detail= "Usuário ou senha incorretos")

        new_access_token = encode_token(user_id_result.obj, 10, key)
        new_refresh_token = encode_token(user_id_result.obj, 1440, key)

        response = JSONResponse({"message":str(user_id_result.message)}, status.HTTP_200_OK)
        response.set_cookie("access-token", new_access_token, secure=True, httponly=True)
        response.set_cookie("refresh-token", new_refresh_token, secure=True, httponly=True)
        
        return response


@cbv(auth_router)
class LogoutController:
    @auth_router.post("/logout/")
    async def logout(self):

        response = JSONResponse({"message": "Log Out"}, status_code= status.HTTP_200_OK)
        response.delete_cookie("refresh-token", secure=True, httponly=True)
        response.delete_cookie("access-token", secure=True, httponly=True)

        return response


