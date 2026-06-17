from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.lifespan_config import LifespanConfig
from middlewares.user_states import SetUserLoginState
from routes.auth_routes import auth_router
from routes.user_routes import user_router
from routes.list_routes import list_router
from routes.review_routes import review_router
from routes.game_routes import game_router

lifespan = LifespanConfig()
app = FastAPI(lifespan = lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # porta padrão do Vite/React
    allow_credentials=True,                   # necessário para cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SetUserLoginState)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(list_router)
app.include_router(review_router)
app.include_router(game_router)
