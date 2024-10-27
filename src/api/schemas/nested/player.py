from pydantic import Field

from api.enums import PlayerStateEnum
from api.schemas.base import JoinLinkSchemaMixin
from api.schemas.lobby import LobbyInDBSchema, LobbyShowSchema
from api.schemas.player import PlayerInDBSchema, PlayerShowSchema
from api.schemas.user import UserInDBSchema, UserShowSchema
from exceptions.service.lobby import (
    NoLeadPlayerInLobbyError,
    TooManyLeadPlayersInLobbyError,
)


class LobbyWithPlayersSchema(LobbyInDBSchema):
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


class LobbyWithLinkSchema(LobbyWithPlayersSchema, JoinLinkSchemaMixin):
    players: list[PlayerInDBSchema]

    @classmethod
    def from_base(
        cls,
        base_lobby: LobbyWithPlayersSchema,
        join_url: str,
    ) -> "LobbyWithLinkSchema":
        """
        Instantiate LobbyWithLinkSchema from lobby schema with players.

        :param base_lobby: lobby schema with players
        :param join_url: url to join lobby
        :return: lobby schema with players and join link
        """
        return cls.model_validate({**base_lobby.model_dump(), "join_url": join_url})


class LobbyWithLinkShowSchema(LobbyShowSchema, JoinLinkSchemaMixin):
    players: list[PlayerShowSchema]


class PlayerWithLobbyUserSchema(PlayerInDBSchema):
    lobby: LobbyInDBSchema
    user: UserInDBSchema


class PlayerWithLinkSchema(PlayerWithLobbyUserSchema, JoinLinkSchemaMixin):
    @classmethod
    def from_base(
        cls,
        base_player: PlayerWithLobbyUserSchema,
        join_url: str,
    ) -> "PlayerWithLinkSchema":
        """
        Instantiate PlayerWithLinkSchema from player schema with lobby and user data.

        :param base_player: player schema with lobby and user data
        :param join_url: url to join lobby
        :return: player schema with lobby, use and join link
        """
        return cls.model_validate({**base_player.model_dump(), "join_url": join_url})


class PlayerWithLinkShowSchema(PlayerShowSchema, JoinLinkSchemaMixin):
    lobby: LobbyShowSchema
    user: UserShowSchema
