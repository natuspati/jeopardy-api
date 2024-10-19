from pydantic import Field

from api.enums import PlayerStateEnum
from api.schemas.base import BaseSchema, FromAttributesMixin, IDSchemaMixin


class BasePlayerSchema(BaseSchema):
    name: str = Field(max_length=20)
    score: int | None = None
    state: PlayerStateEnum
    lobby_id: int
    user_id: int


class PlayerCreateSchema(BasePlayerSchema):
    pass


class LobbyPlayerAddSchema(BaseSchema):
    name: str = Field(max_length=20)


class PlayerInDBSchema(BasePlayerSchema, IDSchemaMixin, FromAttributesMixin):
    pass


class PlayerShowSchema(BasePlayerSchema, IDSchemaMixin):
    pass
