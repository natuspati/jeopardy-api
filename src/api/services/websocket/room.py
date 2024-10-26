from typing import AsyncGenerator, Iterable

from fastapi import WebSocket

from api.messages.base import BaseWebsocketMessage
from api.services.websocket.connection import Connection
from exceptions.service.websocket import (
    WebsocketConnectionExistsError,
    WebsocketConnectionNotExistsError,
)


class Room:
    def __init__(self, room_id: str):
        self._id = room_id
        self._connections: dict[str, Connection] = {}

    @property
    def id(self) -> str:
        """
        Get room id.

        :return: room id
        """
        return self._id

    def get_connection(
        self,
        connection_id: str,
        raise_error: bool = False,
    ) -> Connection | None:
        """
        Fetch connection.

        :param connection_id: connection id
        :param raise_error: whether to error out if connection does not exist
        :return: connection
        """
        connection = self._connections.get(connection_id)
        if not connection and raise_error:
            raise WebsocketConnectionNotExistsError()
        return connection

    async def create_connection(
        self,
        connection_id: str | int,
        websocket: WebSocket,
        disconnect_existing: bool = True,
    ) -> Connection:
        """
        Create a connection.

        :param connection_id: connection id
        :param websocket: websocket connection
        :param disconnect_existing: whether to disconnect existing connection
        :return: created connection
        """
        existing_connection = self.get_connection(connection_id)
        if existing_connection:
            conn_exists_error = WebsocketConnectionExistsError()
            if disconnect_existing:
                await self._remove_connection(
                    connection=existing_connection,
                    code=conn_exists_error.ws_status_code,
                    reason=conn_exists_error.detail,
                )
            else:
                raise conn_exists_error
        new_connection = Connection(connection_id, websocket)
        self._connections[connection_id] = new_connection
        return new_connection

    async def send(
        self,
        message: BaseWebsocketMessage,
        connection_ids: Iterable[str | int] | None = None,
    ) -> None:
        """
        Send message to connections.

        If connection ids are not provided, send message to all connections.

        :param message: message
        :param connection_ids: connection ids
        :return:
        """
        if connection_ids is None:
            connection_ids = self._connections.keys()

        for connection_id in connection_ids:
            connection = self.get_connection(connection_id)
            if connection:
                await connection.send(message)

    async def receive(
        self,
        connection_id: str,
    ) -> AsyncGenerator[dict, None]:
        """
        Receive message from a connection.

        :param connection_id: connection id
        :yield: message
        """
        connection = self.get_connection(connection_id, raise_error=True)
        async with connection:
            async for message in connection:
                yield message

    async def _remove_connection(
        self,
        connection: Connection,
        code: int,
        reason: str | None = None,
    ) -> None:
        await connection.disconnect(code=code, reason=reason)
        self._connections.pop(connection.id)
