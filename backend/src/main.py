from fastapi import FastAPI

from config.lifespan_config import LifespanConfig
from middlewares.user_states import SetUserLoginState
from routes.auth_routes import auth_router
from routes.user_routes import user_router
from routes.list_routes import list_router
from routes.review_routes import review_router

lifespan = LifespanConfig()
app = FastAPI(lifespan = lifespan)

app.add_middleware(SetUserLoginState)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(list_router)
app.include_router(review_router)
