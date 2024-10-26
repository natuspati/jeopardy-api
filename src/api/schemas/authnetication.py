from pydantic import Field

from api.schemas.base import BaseSchema


class UserInTokenSchema(BaseSchema):
    user_id: int
    username: str = Field(alias="sub")
    is_active: bool


class TokenSchema(BaseSchema):
    access_token: str
    token_type: str
