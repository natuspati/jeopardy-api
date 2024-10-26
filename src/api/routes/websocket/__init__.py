"""Websocket routes module."""

from fastapi import APIRouter

from api.routes.websocket.lobby import lobby_router

ws_router = APIRouter(prefix="/ws", tags=["Websocket"])
ws_router.include_router(lobby_router)
