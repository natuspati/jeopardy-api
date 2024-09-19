from pydantic import Field

from api.enums import PlayerStateEnum
from api.schemas.base import BaseSchema, FromAttributesMixin, IDSchemaMixin


class BasePlayerSchema(BaseSchema):
    name: str = Field(max_length=20)
    score: int | None = None
    state: PlayerStateEnum


class PlayerInDBSchema(BasePlayerSchema, IDSchemaMixin, FromAttributesMixin):
    lobby_id: int
    user_id: int


class PlayerShowSchema(BasePlayerSchema, IDSchemaMixin):
    lobby_id: int
    user_id: int
