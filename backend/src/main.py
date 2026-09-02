from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import LifespanConfig
from middlewares import SetUserLoginState
from routes import auth_router, game_router, list_router, review_router, user_router
from utils.utils import QueryError

lifespan = LifespanConfig()
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(QueryError)
async def query_error_handler(request: Request, exc: QueryError):
    return JSONResponse({"message": exc.message}, exc.status_code)

@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    return JSONResponse(str(exc), 500)

app.add_middleware(SetUserLoginState)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(list_router)
app.include_router(review_router)
app.include_router(game_router)
