"""Version 1 routes module."""

from fastapi import APIRouter

from api.routes.v1.lobby import lobby_router
from api.routes.v1.token import token_router
from api.routes.v1.user import user_router

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(token_router)
api_v1_router.include_router(user_router)
api_v1_router.include_router(lobby_router)
