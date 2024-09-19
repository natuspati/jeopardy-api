from datetime import datetime

from pydantic import Field

from api.schemas.base import (
    BaseSchema,
    CreatedAtSchemaMixin,
    FromAttributesMixin,
    IDSchemaMixin,
    OneFieldSetSchemaMixin,
)
from api.schemas.pagination import PaginatedResultsSchema


class BaseUserSchema(BaseSchema):
    username: str = Field(max_length=50)


class UserCreateSchema(BaseUserSchema):
    pass


class UserUpdateSchema(BaseUserSchema, OneFieldSetSchemaMixin):
    pass


class UserInDBSchema(
    BaseUserSchema,
    IDSchemaMixin,
    CreatedAtSchemaMixin,
    FromAttributesMixin,
):
    password: str = Field(max_length=100)
    is_active: bool
    modified_at: datetime


class UserShowSchema(BaseUserSchema, IDSchemaMixin, CreatedAtSchemaMixin):
    modified_at: datetime


class PaginatedUsersInDBSchema(PaginatedResultsSchema):
    items: list[UserInDBSchema]


class PaginatedUsersShowSchema(PaginatedResultsSchema):
    items: list[UserShowSchema]
