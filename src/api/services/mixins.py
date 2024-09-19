from typing import Iterable

from pydantic import ValidationError

from api.schemas.base import BaseSchema
from database.base_model import BaseDBModel
from exceptions.module.schema import SchemaValidationError


class DBModelValidatorMixin:
    @classmethod
    def validate(
        cls,
        db_data: BaseDBModel | Iterable[BaseDBModel] | None,
        schema: type[BaseSchema],
    ):
        """
        Validate an instance or a list of SQLAlchemy models to Pydantic model.

        :param db_data: instance or list of SQLAlchemy models
        :param schema: Pydantic model
        :return: instance or list of Pydantic models
        """
        if db_data is not None:
            if isinstance(db_data, BaseDBModel):
                return cls._validate_db_model(
                    db_model=db_data,
                    schema=schema,
                )
            return cls._validate_db_models(
                db_models=db_data,
                schema=schema,
            )

    @classmethod
    def _validate_db_model(
        cls,
        db_model: BaseDBModel,
        schema: type[BaseSchema],
    ) -> BaseSchema:
        try:
            return schema.model_validate(db_model)
        except ValidationError as error:
            raise SchemaValidationError(error) from error

    @classmethod
    def _validate_db_models(
        cls,
        db_models: Iterable[BaseDBModel],
        schema: type[BaseSchema],
    ) -> list[BaseSchema]:
        try:
            return [schema.model_validate(model) for model in db_models]
        except ValidationError as error:
            raise SchemaValidationError(error) from error
