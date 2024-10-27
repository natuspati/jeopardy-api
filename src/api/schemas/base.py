from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator

from exceptions.service.schema import AllFieldsUnsetValidationError


class BaseSchema(BaseModel):
    pass


class FromAttributesMixin:
    model_config = ConfigDict(from_attributes=True)


class IDSchemaMixin:
    id: int


class CreatedAtSchemaMixin:
    created_at: datetime


class OneFieldSetSchemaMixin:
    @model_validator(mode="after")
    @classmethod
    def check_at_least_one_field_is_set(cls, values: BaseModel):
        """
        Check if schema has at least one field set.

        :param values: validated schema
        :return: schema with at least one field set
        """
        if not values.model_fields_set:
            raise AllFieldsUnsetValidationError()
        return values


class JoinLinkSchemaMixin:
    join_url: str


class BaseDBSchema(BaseSchema, FromAttributesMixin, IDSchemaMixin):
    pass


class BaseAssociationDBSchema(BaseSchema, FromAttributesMixin):
    pass
