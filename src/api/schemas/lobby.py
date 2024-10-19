from pydantic import Field

from api.schemas.base import (
    BaseSchema,
    CreatedAtSchemaMixin,
    FromAttributesMixin,
    IDSchemaMixin,
)
from api.schemas.pagination import PaginatedResultsSchema


class BaseLobbySchema(BaseSchema):
    name: str = Field(max_length=50)


class LobbyCreateSchema(BaseLobbySchema):
    pass


class LobbyPlayerCreateSchema(BaseSchema):
    lobby_name: str = Field(max_length=50)
    player_name: str = Field(max_length=20)


class LobbyInDBSchema(
    BaseLobbySchema,
    IDSchemaMixin,
    CreatedAtSchemaMixin,
    FromAttributesMixin,
):
    pass


class LobbyShowSchema(BaseLobbySchema, IDSchemaMixin, CreatedAtSchemaMixin):
    pass


class PaginatedLobbiesSchema(PaginatedResultsSchema):
    items: list[LobbyInDBSchema]
