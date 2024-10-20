from fastapi import status

from exceptions.service.base import BaseServiceError


class LobbyError(BaseServiceError):
    detail = "Operation on Lobby API failed"


class PlayerLobbyDoesNotMatchError(LobbyError):
    detail = "Player lobby does not match lobby"
    status_code = status.HTTP_400_BAD_REQUEST


class NoLeadPlayerInLobbyError(LobbyError):
    detail = "No lead player in lobby"


class TooManyLeadPlayersInLobbyError(LobbyError):
    detail = "Too many lead players in lobby"
