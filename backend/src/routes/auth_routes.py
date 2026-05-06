from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse

from models.schemas import Auth_login
from services.security_services import passwords_match, encode_token
from services.db_services import DB_read_user_cred
from utils.dependencies import get_conn


auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login")
async def login(request: Request, user: Auth_login, conn = Depends(get_conn)):

    result = await DB_read_user_cred(conn, user)

    if not result.success:
        return JSONResponse({"message":str(result.message)}, status.HTTP_400_BAD_REQUEST)

    if not passwords_match(result.obj["password"], user.password):
        return JSONResponse({"message":"Usuário ou senha incorretos"}, status.HTTP_401_UNAUTHORIZED)

    key = request.app.state.jwt_key
    new_access_token = encode_token(result.obj["user_id"], 10, key)
    new_refresh_token = encode_token(result.obj["user_id"], 1440, key)

    response = JSONResponse({"message":str(result.message)}, status.HTTP_202_ACCEPTED)
    response.set_cookie("access-token", new_access_token, secure=True, httponly=True)
    response.set_cookie("refresh-token", new_refresh_token, secure=True, httponly=True)
    
    return response


@auth_router.post("/logout")
async def logout():

    response = JSONResponse({"message": "Log Out"}, status_code= status.HTTP_202_ACCEPTED)
    response.delete_cookie("refresh-token", secure=True, httponly=True)

    return response


