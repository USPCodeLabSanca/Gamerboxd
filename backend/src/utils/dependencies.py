from fastapi import Request, HTTPException

async def get_conn(request: Request):
    pool = request.app.state.pool
    
    async with pool.acquire() as conn:
        yield conn

def require_login(request: Request) -> str:
    login = request.state.user_login
    if not login["logged_in"]:
        raise HTTPException(401, "É necessário fazer login paar esta ação")
    return login["user_id"]

def require_key(request: Request) -> str:
    return request.app.state.jwt_key
