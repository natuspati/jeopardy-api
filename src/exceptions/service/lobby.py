from fastapi import status

from exceptions.service.base import BaseServiceError


class LobbyError(BaseServiceError):
    detail = "Operation on Lobby API failed"
    status_code = status.HTTP_400_BAD_REQUEST


class PlayerLobbyDoesNotMatchError(LobbyError):
    detail = "Player lobby does not match lobby"
