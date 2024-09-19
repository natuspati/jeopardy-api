from datetime import timedelta

from sqlalchemy import delete, insert

from database.migrations.data.commons.timestamps import DEFAULT_DATE_TIME
from database.models.lobby import LobbyModel

LOBBY_COUNT = 3

lobbies = []
lobby_ids = []
for i in range(1, LOBBY_COUNT + 1):
    lobby_creation_time = DEFAULT_DATE_TIME + timedelta(days=30) + timedelta(days=i)
    lobby = {"id": i, "name": f"Lobby {i}", "created_at": lobby_creation_time}
    lobbies.append(lobby)
    lobby_ids.append(lobby["id"])

CREATE_LOBBIES_QUERIES = (insert(LobbyModel).values(lobbies),)


DELETE_LOBBIES_QUERIES = (delete(LobbyModel).where(LobbyModel.id.in_(lobby_ids)),)
