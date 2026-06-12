from fastapi import Request, HTTPException

async def get_conn(request: Request):
    pool = request.app.state.internal_pool
    
    async with pool.acquire() as conn:
        yield conn

async def get_exconn(request: Request):
    yield request.app.state.external_pool

def require_login(request: Request) -> str:
    login = request.state.user_login
    if not login["logged_in"]:
        raise HTTPException(401, "É necessário fazer login para esta ação")
    return login["user_id"]

def get_key(request: Request) -> str:
    return request.app.state.jwt_key


def get_rawg(request: Request) -> str:
    return  request.app.state.rawg_key 
