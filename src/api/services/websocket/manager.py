from fastapi import WebSocket

from api.services.websocket.connection import Connection
from api.services.websocket.room import Room
from exceptions.service.websocket import (
    WebsocketRoomExistsError,
    WebsocketRoomNotExistsError,
)


class ConnectionManager:
    def __init__(self):
        self._rooms: dict[str, Room] = {}

    def get_room(self, room_id: str, raise_error: bool = False) -> Room | None:
        """
        Get room.

        :param room_id: room id
        :param raise_error: whether to error out if room does not exist
        :return: room
        """
        room = self._rooms.get(room_id)
        if not room and raise_error:
            raise WebsocketRoomNotExistsError()
        return room

    def create_connection(
        self,
        room_id: str,
        connection_id: str,
        websocket: WebSocket,
        disconnect_existing: bool = True,
    ) -> Connection:
        """
        Create a connection in the room.

        If room does not exist, create a new room.

        :param room_id: room id
        :param connection_id: connection id
        :param websocket: websocket connection
        :param disconnect_existing: whether to disconnect existing connection
        :return: connection
        """
        room = self.get_or_create_room(room_id)
        return room.create_connection(connection_id, websocket, disconnect_existing)

    def get_or_create_room(self, room_id: str) -> Room:
        """
        Get or create a room.

        :param room_id: room id
        :return: room
        """
        existing_room = self.get_room(room_id)
        if not existing_room:
            return self._create_room(room_id)
        return existing_room

    def _create_room(self, room_id: str) -> Room:
        if self.get_room(room_id):
            raise WebsocketRoomExistsError()
        new_room = Room(room_id)
        self._rooms[room_id] = new_room
        return new_room


ws_conn_manager = ConnectionManager()
