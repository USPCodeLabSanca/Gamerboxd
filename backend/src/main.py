from aiohttp.client_exceptions import ContentTypeError
from dotenv import dotenv_values
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import LifespanConfig
from .middlewares import *
from .routes import auth_router, game_router, list_router, review_router, user_router
from .utils.errors import QueryError

env = dotenv_values(".env")

lifespan = LifespanConfig(env)
app = FastAPI(lifespan=lifespan)


@app.exception_handler(QueryError)
async def caught_error_handler(request: Request, exc: QueryError):
    """Trata erros que foram encontrados ao longo da execução do app"""
    if exc.status_code == 500:
        print(f"caught: {exc.message}")
    return JSONResponse({"message": exc.message}, exc.status_code)


@app.exception_handler(ContentTypeError)
async def rawg_error_handler(request: Request, exc: ContentTypeError):
    """Trata erros da rawg api"""
    return JSONResponse({"message": str(exc)}, 502)


@app.exception_handler(Exception)
async def uncaught_error_handler(request: Request, exc: Exception):
    """Trata erros que não foram encontrados ao longo da execução do app"""
    print(f"uncaught: {str(exc)}")
    return JSONResponse({"message": str(exc)}, 500)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[env["FRONT_URL"]],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SetUserLoginStateMiddleware)
app.add_middleware(TimeoutMiddleware)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(list_router)
app.include_router(review_router)
app.include_router(game_router)

