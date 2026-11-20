from datetime import datetime, timezone
from fastapi import Request
from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware

from ..services.security_services import add_cookie, decode_token


class SetUserLoginStateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """Avalia e armazena o status do login do usuário no request.state"""

        # Avalia o usuário e armazena o seu status no request.state
        user_id, needs_new_token = self.assess_user(request)
        user_login = {
            "logged_in": False if user_id == None else True,
            "user_id": user_id
        }
        request.state.user_login = user_login

        # Encaminha para a rota requisitada
        response = await call_next(request)

        # Se o status do usuário for login expirado, renova o login dele antes de devolver a resposta
        if needs_new_token:
            response = add_cookie(response, request.app.state.jwt_config, "access-token", user_id)

        return response
    
    def assess_user(self, request: Request):
        """Avalia o estado do usuário a partir dos cookies da requisição"""

        user_cookies = request.cookies

        # Verifica se o usuário tem os 2 tokens de autenticação
        if any(standard_cookie not in request.cookies for standard_cookie in ["access-token", "refresh-token"]):
            return None, False
        
        key = request.app.state.jwt_config["key"]

        try:
            # Recupera os tokens de autenticação do usuário
            claims = {
                "issuer": request.app.state.jwt_config["iss"],
                "audience": request.app.state.jwt_config["aud"]
            }
            decoded_access_token = decode_token(user_cookies["access-token"], key, **claims)
            decoded_refresh_token = decode_token(user_cookies["refresh-token"], key, **claims)

        except jwt.JWTError as e:
            return None, False
        
        now = datetime.now(tz=timezone.utc)
        user_id = decoded_access_token["sub"]

        # Verifica se o refresh token tá vencido, caso sim: deslogar
        if self.is_token_expired(decoded_refresh_token, now):
            return None, False
        
        # Verifica se o access token tá vencido, caso sim: renovar login
        needs_new_token = self.is_token_expired(decoded_access_token, now)

        return user_id, needs_new_token


    def is_token_expired(self, token, now):
        """Verifica se um token expirou"""
        
        token_exp = datetime.fromtimestamp(token["exp"], tz=timezone.utc)
        return (token_exp < now)

