from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from ..models.schemas.user import UserAuth
from ..services.security_services import passwords_match, add_cookie, remove_cookie
from ..services.db_services.user import DB_read_user_column
from ..utils import errors as err
from . import dependencies as dep


auth_router = APIRouter(prefix= "/auth", tags=["auth"])


@auth_router.post("/login")
async def login(user: UserAuth, conn = Depends(dep.get_conn), jwt_config = Depends(dep.get_jwt_config)):
    """Autentica o usuário com email ou username e senha"""

    user_id = await DB_read_user_column(conn, "id", username=user.email_or_username, email=user.email_or_username)

    if user_id is None:
        raise err.QueryError(400, "Usuário ou senha incorretos")

    stored_password = await DB_read_user_column(conn, "password", user_id=user_id)

    if not passwords_match(stored_password, user.password):
        raise err.QueryError(400, "Usuário ou senha incorretos")

    response = JSONResponse({"message":"Login feito com sucesso!", "user_id": user_id})
    response = add_cookie(response, jwt_config, "access-token", user_id)
    response = add_cookie(response, jwt_config, "refresh-token", user_id)
    
    return response


@auth_router.delete("/login")
async def logout(jwt_config = Depends(dep.get_jwt_config)):
    """Encerra a sessão do usuário removendo os cookies de autenticação"""

    response = JSONResponse({"message": "Logout feito com sucesso!"})
    response = remove_cookie(response, jwt_config, "refresh-token")
    response = remove_cookie(response, jwt_config, "access-token")

    return response


@auth_router.get("/me")
async def who_am_i(user_id: str = Depends(dep.require_login), conn = Depends(dep.get_conn)):
    """Envia o user_id do usuário de volta para o frontend"""

    user_email = await DB_read_user_column(conn, column="email", user_id=user_id)

    return JSONResponse({"message": "Encontramos o usuário!", "user_id": user_id, "email":user_email})

