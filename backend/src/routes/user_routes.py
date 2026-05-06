from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse

from models.schemas import *
from services.security_services import *
from services.db_services import *
from utils.dependencies import get_conn

user_router = APIRouter(prefix="/user", tags=["user"])

@user_router.post("/")
async def new_account(request: Request, user: User, conn = Depends(get_conn)):

    # Validação do username
    user.username = user.username.strip()

    username_length = len(user.username)
    username_has_right_length = (username_length) < 25 and (username_length > 3)

    if not username_has_right_length:
        return JSONResponse(
            {"message": f'O username deve ter entre 4 e 24 caracteres'},
            status_code= status.HTTP_400_BAD_REQUEST
        )
        
    username_exists_result = await DB_read_username_already_exists(conn, user)

    if not username_exists_result.success:
        return JSONResponse({"message": username_exists_result.message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if username_exists_result.obj:
        return JSONResponse(
                {"message": f'O username "{user.username}" já está sendo utilizado'},
                status_code= status.HTTP_400_BAD_REQUEST
            )
    
    # Validação do email
    user.email = user.email.strip()

    if '@' not in user.email:
        return JSONResponse({"message": "Email inválido"}, status.HTTP_400_BAD_REQUEST)
    
    email_exists_result = await DB_read_email_already_exists(conn, user)
    
    if not username_exists_result.success:
        return JSONResponse({"message": username_exists_result.message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if email_exists_result.obj:
        return JSONResponse(
                {"message": "Este email já está atrelado a outra conta"},
                status_code= status.HTTP_400_BAD_REQUEST
            )

    # Validação da senha    
    user.password = user.password.strip()
    password_length = len(user.password)

    pwd_has_right_length = (password_length) < 65 and (password_length > 7)
    pwd_has_number = any(char.isdigit() for char in user.password)
    pwd_has_special = any(not char.isalnum() for char in user.password)
    pwd_has_capital = any(char.isupper() for char in user.password)
    pwd_has_lower = any(char.islower() for char in user.password)
    
    if not any([pwd_has_capital, pwd_has_lower, pwd_has_number, pwd_has_special, pwd_has_right_length]):
        return JSONResponse(
            {"message": f'A senha deve conter entre 8 a 64 caractéres, com pelo menos uma letra minúscula, uma letra maiúscula, um número e um símbolo'},
            status_code= status.HTTP_400_BAD_REQUEST
    )
    
    user.password = encrypt_password(user.password)

    account_creation_result = await DB_create_account(conn, user)

    if not account_creation_result.success:
        return JSONResponse({"message": account_creation_result.message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Cria a lista de favoritos
    favorites_list = List(
        creator = account_creation_result.obj,
        name = "Favoritos",
        description = "Meus games favoritos",
        is_private = True
        )
    
    favorites_list_creation_result = await DB_create_list(conn, favorites_list)
    if not favorites_list_creation_result.success:
        return JSONResponse({"message": favorites_list_creation_result.message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Cria a lista de completados
    finished_list = List(
        creator = account_creation_result.obj,
        name = "Completados",
        description = "Meus games completados",
        is_private = True
    )

    finished_list_creation_result = await DB_create_list(conn, finished_list)
    if not finished_list_creation_result.success:
        return JSONResponse({"message": favorites_list_creation_result.message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    key = request.app.state.jwt_key
    new_access_token = encode_token(account_creation_result.obj, 10, key)
    new_refresh_token = encode_token(account_creation_result.obj, 1440, key)

    response = JSONResponse({"message":account_creation_result.message}, status.HTTP_202_ACCEPTED)
    response.set_cookie("access-token", new_access_token, secure=True, httponly=True)
    response.set_cookie("refresh-token", new_refresh_token, secure=True, httponly=True)
    
    return response
