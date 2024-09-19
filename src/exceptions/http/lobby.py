from fastapi import status

from exceptions.http.base import BaseApiError


class LobbyApiError(BaseApiError):
    detail = "Operation on Lobby API failed"
    status_code = status.HTTP_400_BAD_REQUEST


class PlayerLobbyDoesNotMatchApiError(LobbyApiError):
    detail = "Player lobby does not match lobby"
