from fastapi import status
from pydantic import ValidationError

from exceptions.service.base import BaseServiceError


class BaseSchemaError(BaseServiceError):
    detail: str = "Schema error"


class SchemaValidationError(BaseSchemaError):
    _error_message_template = (
        "Validation errors for schema {schema_name}, count: {error_count}.\n"
    )
    _single_error_message_template = (
        "\tError no. {error_number}, type: {error_type}, location: {error_location}.\n"
        + "\tMessage: {error_message}.\n"
        + "\tInput: {error_input}.\n"
    )

    def __init__(self, error: ValidationError):
        super().__init__(detail=self._format_pydantic_errors(error))

    @classmethod
    def _format_pydantic_errors(cls, error: ValidationError) -> str:
        error_message = cls._error_message_template.format(
            schema_name=error.title,
            error_count=error.error_count(),
        )
        for err_number, single_error in enumerate(error.errors()):
            single_error_message = cls._single_error_message_template.format(
                error_number=err_number + 1,
                error_type=single_error.get("type"),
                error_location=single_error.get("loc"),
                error_message=single_error.get("msg"),
                error_input=single_error.get("input"),
            )
            error_message += single_error_message
        return error_message


class SchemaInputError(BaseSchemaError):
    detail: str = "Schema input error"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class AllFieldsUnsetValidationError(BaseSchemaError):
    detail = "At least one field must be set"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
