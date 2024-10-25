from types import TracebackType
from typing import AsyncGenerator

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect, WebSocketState

from api.schemas.websocket import BaseWebsocketMessageSchema
from exceptions.service.websocket import WebsocketInvalidStateError


class Connection:
    def __init__(self, connection_id: str, websocket: WebSocket):
        self._id = connection_id
        self._websocket = websocket

    async def __aenter__(self):
        await self._websocket.accept()
        return self

    async def __aexit__(
        self,
        exc_type: type | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ):
        await self._websocket.close()

    async def __aiter__(self) -> AsyncGenerator[dict, None]:
        self._check_client_state()
        while True:
            try:
                yield await self._websocket.receive_json()
            except WebSocketDisconnect:
                break

    async def send(self, message: BaseWebsocketMessageSchema) -> None:
        self._check_client_state()
        await self._websocket.send_json(message.model_dump())

    def _check_client_state(
        self,
        state: WebSocketState = WebSocketState.CONNECTED,
        raise_error: bool = True,
    ) -> bool:
        if self._websocket.client_state == state:
            return True
        if raise_error:
            raise WebsocketInvalidStateError()
        return False
