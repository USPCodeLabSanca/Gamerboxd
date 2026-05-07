from fastapi import Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from models.schemas import *
from services.security_services import *
from services.db_services import *
from utils.dependencies import get_conn, require_login

review_router = InferringRouter(prefix="/review", tags=["review"])