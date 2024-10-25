"""Websocket routes module."""

from fastapi import APIRouter

ws_router = APIRouter(prefix="/ws", tags=["Websocket"])
