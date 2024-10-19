from typing import Any

from pydantic import model_validator

from api.schemas.base import BaseSchema


class ErrorSchema(BaseSchema):
    detail: str


class ValidationInputErrorSchema(BaseSchema):
    type: str
    loc: tuple[str, str]
    msg: str
    input: str | None
    ctx: dict[str, Any] | None = None


class ValidationInputErrorsSchema(BaseSchema):
    errors: list[ValidationInputErrorSchema]
    count: int

    @model_validator(mode="before")
    @classmethod
    def calculate_error_count(cls, input_data: dict) -> dict:
        """
        Calculate error count.

        :param input_data: input data
        :return: input data with error count
        """
        validation_errors = input_data.get("errors")
        if validation_errors:
            input_data["count"] = len(validation_errors)
        return input_data
