from types import TracebackType
from typing import AsyncGenerator

from fastapi import WebSocket, status
from starlette.websockets import WebSocketDisconnect, WebSocketState

from api.messages.base import BaseWebsocketMessage
from exceptions.service.base import BaseServiceError
from exceptions.service.websocket import WebsocketInvalidStateError


class Connection:
    def __init__(self, connection_id: str, websocket: WebSocket):
        self._id = connection_id
        self._websocket = websocket

    @property
    def id(self) -> str:
        """
        Get connection id.

        :return: connection id
        """
        return self._id

    @property
    def client_state(self) -> WebSocketState:
        """
        Get client connection state.

        :return: connection state
        """
        return self._websocket.client_state

    async def __aenter__(self):
        """
        Connect to websocket.

        :return:
        """
        await self._websocket.accept()
        return self

    async def __aexit__(
        self,
        exc_type: type | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ):
        """
        Disconnect from websocket.

        :param exc_type: error type if present
        :param exc: error if present
        :param tb: traceback if present
        :return:
        """
        code = getattr(exc, "ws_status_code", BaseServiceError.ws_status_code)
        reason = getattr(exc, "detail", BaseServiceError.detail)
        await self.disconnect(code=code, reason=reason)

    async def __aiter__(self) -> AsyncGenerator[dict, None]:
        """
        Iterate over messages in websocket connection.

        :yield: message as dictionary
        """
        self._check_client_state()
        while True:
            try:
                yield await self._websocket.receive_json()
            except WebSocketDisconnect:
                break

    async def disconnect(
        self,
        code: int = status.WS_1001_GOING_AWAY,
        reason: str | None = None,
    ) -> None:
        """
        Disconnect from websocket.

        :return:
        """
        if not self._check_client_state(WebSocketState.DISCONNECTED, raise_error=False):
            await self._websocket.close(
                code=code,
                reason=reason,
            )

    async def send(self, message: BaseWebsocketMessage) -> None:
        """
        Send message to websocket connection.

        :param message: message
        :return:
        """
        self._check_client_state()
        await self._websocket.send_json(message.to_dict())

    def _check_client_state(
        self,
        state: WebSocketState = WebSocketState.CONNECTED,
        raise_error: bool = True,
    ) -> bool:
        if self.client_state == state:
            return True
        if raise_error:
            raise WebsocketInvalidStateError()
        return False
