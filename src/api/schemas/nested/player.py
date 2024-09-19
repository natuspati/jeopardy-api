from pydantic import Field

from api.schemas.lobby import LobbyInDBSchema, LobbyShowSchema
from api.schemas.player import PlayerInDBSchema, PlayerShowSchema
from api.schemas.user import UserInDBSchema, UserShowSchema


class LobbyWithPlayersInDBSchema(LobbyInDBSchema):
    players: list[PlayerInDBSchema] = Field(validation_alias="player_associations")


class LobbyWithPlayersScowSchema(LobbyShowSchema):
    players: list[PlayerShowSchema]


class PlayerWithLobbyUserInDBSchema(PlayerInDBSchema):
    lobby: LobbyInDBSchema
    user: UserInDBSchema


class PlayerWithLobbyUseShowSchema(PlayerShowSchema):
    lobby: LobbyShowSchema
    user: UserShowSchema
