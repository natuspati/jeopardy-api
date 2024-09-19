from pydantic import Field

from api.schemas.base import BaseSchema


class TokenDataSchema(BaseSchema):
    user_id: int
    username: str = Field(alias="sub")


class TokenSchema(BaseSchema):
    access_token: str
    token_type: str
