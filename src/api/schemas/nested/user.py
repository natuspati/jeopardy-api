from pydantic import Field, field_validator

from api.schemas.lobby import LobbyInDBSchema, LobbyShowSchema
from api.schemas.player import PlayerInDBSchema, PlayerShowSchema
from api.schemas.user import UserInDBSchema, UserShowSchema
from database.models.lobby import LobbyModel


class UserWithLobbiesInDBSchema(UserInDBSchema):
    lobbies: list[LobbyInDBSchema]
    players: list[PlayerInDBSchema] = Field(validation_alias="player_associations")

    @field_validator("lobbies", mode="before")
    @classmethod
    def sort_lobbies(cls, lobbies: list[LobbyModel]) -> list[LobbyModel]:
        """
        Sort lobbies in descending order.

        :param lobbies: list of SQLAlchemy models
        :return: sorted list of lobby models
        """
        return sorted(lobbies, key=lambda lobby: lobby.created_at, reverse=True)

    def has_lobby(self, lobby_id: int) -> bool:
        """
        Check if user has lobby with given id.

        :param lobby_id: lobby id
        :return: whether user has lobby with given id
        """
        return any(lobby.id == lobby_id for lobby in self.lobbies)

    def has_player(self, player_id: int) -> bool:
        """
        Check if user has player with given id.

        :param player_id: player id
        :return: whether user has player with given id
        """
        return any(player.id == player_id for player in self.players)


class UserWithLobbiesShowSchema(UserShowSchema):
    lobbies: list[LobbyShowSchema] = Field(
        description="List of lobbies that the user participates in, descending order.",
    )
    players: list[PlayerShowSchema] = Field(
        description="List of players that the user created.",
    )
