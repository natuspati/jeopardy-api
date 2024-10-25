from typing import AsyncGenerator, Iterable

from fastapi import WebSocket

from api.schemas.websocket import BaseWebsocketMessageSchema
from api.services.websocket.connection import Connection
from exceptions.service.websocket import (
    WebsocketConnectionExistsError,
    WebsocketConnectionNotExistsError,
)


class Room:
    def __init__(self, room_id: str):
        self._id = room_id
        self._connections: dict[str, Connection] = {}

    def get_connection(
        self,
        connection_id: str,
        raise_error: bool = False,
    ) -> Connection | None:
        """
        Fetch connection.

        :param connection_id: connection id
        :param raise_error: whether to raise exception if connection does not exist, False by default
        :return: connection
        """
        connection = self._connections.get(connection_id)
        if not connection and raise_error:
            raise WebsocketConnectionNotExistsError()
        return connection

    def create_connection(
        self,
        connection_id: str,
        websocket: WebSocket,
        disconnect_existing: bool = True,
    ) -> Connection:
        """
        Create a connection.

        :param connection_id: connection id
        :param websocket: websocket connection
        :param disconnect_existing: whether to disconnect existing connection, True by default
        :return: created connection
        """
        if existing_connection := self.get_connection(connection_id):
            if disconnect_existing:
                raise WebsocketConnectionExistsError()
            return existing_connection
        new_connection = Connection(connection_id, websocket)
        self._connections[connection_id] = new_connection
        return new_connection

    async def send(
        self,
        message: BaseWebsocketMessageSchema,
        connection_ids: Iterable[str] | None = None,
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
