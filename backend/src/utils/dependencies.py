from fastapi import Request

async def get_conn(request: Request):
    pool = request.app.state.pool
    
    async with pool.acquire() as conn:
        yield conn

    