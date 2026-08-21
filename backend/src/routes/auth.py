from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from models.schemas import UserAuth
from services.security_services import passwords_match, encode_token
from services.db_services import DB_read_user_column
from utils.dependencies import get_conn, get_key
from utils.utils import QueryError


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login")
async def login(user: UserAuth, conn = Depends(get_conn), key = Depends(get_key)):
    user_id = await DB_read_user_column(conn, "id", username=user.email_or_username, email=user.email_or_username)

    if user_id is None:
        raise QueryError(400, "Usuário ou senha incorretos")

    stored_password = await DB_read_user_column(conn, "password", user_id=user_id)

    if not passwords_match(stored_password, user.password):
        raise QueryError(400, "Usuário ou senha incorretos")

    new_access_token = encode_token(user_id, 10, key)
    new_refresh_token = encode_token(user_id, 1440, key)

    response = JSONResponse({"message":"Login feito com sucesso"})
    response.set_cookie("access-token", new_access_token, secure=True, httponly=True)
    response.set_cookie("refresh-token", new_refresh_token, secure=True, httponly=True)
    
    return response


@auth_router.post("/logout")
async def logout():

    response = JSONResponse({"message": "Logout feito com sucesso"})
    response.delete_cookie("refresh-token", secure=True, httponly=True)
    response.delete_cookie("access-token", secure=True, httponly=True)

    return response


