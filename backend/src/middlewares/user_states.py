from datetime import datetime, timezone
from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware

from services.security_services import encode_token, decode_token


class SetUserLoginState(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
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
            key = request.app.state.jwt_key
            new_token = encode_token(user_id, 10, key)
            response.set_cookie("access-token", new_token)

        return response
    
    def assess_user(self, request):
        """Avalia o estado do usuário a partir dos cookies da requisição"""

        user_cookies = request.cookies

        # Verifica se o usuário tem os 2 tokens de autenticação
        if ("access-token" not in user_cookies) or ("refresh-token" not in user_cookies):
            return None, False
        
        key = request.app.state.jwt_key

        try:
            # Recupera os tokens de autenticação do usuário
            decoded_access_token = decode_token(user_cookies, "access-token", key)
            decoded_refresh_token = decode_token(user_cookies, "refresh-token", key)

        except jwt.JWTError:
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
        """Verifica a data de vencimento de um token"""
        
        token_exp = datetime.fromtimestamp(token["exp"], tz=timezone.utc)
        return (token_exp < now)

