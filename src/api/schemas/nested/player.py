from pydantic import Field

from api.enums import PlayerStateEnum
from api.schemas.lobby import LobbyInDBSchema, LobbyShowSchema
from api.schemas.player import PlayerInDBSchema, PlayerShowSchema
from api.schemas.user import UserInDBSchema, UserShowSchema
from exceptions.service.lobby import (
    NoLeadPlayerInLobbyError,
    TooManyLeadPlayersInLobbyError,
)


class LobbyWithPlayersInDBSchema(LobbyInDBSchema):
    players: list[PlayerInDBSchema] = Field(validation_alias="player_associations")

    def get_lead(self) -> PlayerInDBSchema:
        """
        Get lead player.

        :return: lead player
        """
        players = self.get_players_by_state(PlayerStateEnum.lead)
        if not players:
            raise NoLeadPlayerInLobbyError()
        if len(players) > 1:
            raise TooManyLeadPlayersInLobbyError()
        return players[0]

    def get_players_by_state(self, state: PlayerStateEnum) -> list[PlayerInDBSchema]:
        """
        Get players by state.

        :param state: player state
        :return: players with given state
        """
        return [player for player in self.players if player.state == state]


class LobbyWithPlayersScowSchema(LobbyShowSchema):
    players: list[PlayerShowSchema]


class PlayerWithLobbyUserInDBSchema(PlayerInDBSchema):
    lobby: LobbyInDBSchema
    user: UserInDBSchema


class PlayerWithLobbyUserShowSchema(PlayerShowSchema):
    lobby: LobbyShowSchema
    user: UserShowSchema
