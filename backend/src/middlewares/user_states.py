from datetime import datetime, timezone
from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware

from services.security_services import encode_token, decode_token


class SetUserLoginState(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):

        user_id, needs_new_token = self.assess_user(request)

        request.state.user_login = "NOT_LOGGED" if user_id == None else f"LOGGED_{user_id}"
        response = await call_next(request)
        
        if needs_new_token:
            key = request.app.state.jwt_key
            new_token = encode_token(user_id, 10, key)
            response.set_cookie = {"access-token": new_token}

        return response
    
    def assess_user(self, request):
        user_cookies = request.cookies

        # Verifica se o usuário tem os token de autenticação
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

        # Verifica se o refresh token tá vencido
        if self.is_token_expired(decoded_refresh_token, now):
            return None, False
        
        # Verifica se o access token tá vencido
        needs_new_token = self.is_token_expired(decoded_access_token, now)

        return user_id, needs_new_token
    
    def is_token_expired(self, token, now):
        token_exp = datetime.fromtimestamp(token["exp"], tz=timezone.utc)
        return (token_exp < now)

