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


class UserWithLobbiesShowSchema(UserShowSchema):
    lobbies: list[LobbyShowSchema] = Field(
        description="List of lobbies that the user participates in, descending order.",
    )
    players: list[PlayerShowSchema] = Field(
        description="List of players that the user created.",
    )
