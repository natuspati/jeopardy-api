from fastapi import status

from api.schemas.base import BaseSchema
from api.schemas.error import ErrorSchema, ValidationInputErrorsSchema

REQUEST_ERROR_RESPONSE = (status.HTTP_400_BAD_REQUEST, "Invalid request parameters")
UNAUTHORIZED_RESPONSE = (
    status.HTTP_401_UNAUTHORIZED,
    "Invalid authentication credentials",
)
FORBIDDEN_RESPONSE = (status.HTTP_403_FORBIDDEN, "Invalid authorization")
INTERNAL_ERROR_RESPONSE = (
    status.HTTP_500_INTERNAL_SERVER_ERROR,
    "Internal server error",
)


def generate_responses(
    *errors: tuple[int, str],
) -> dict[int, dict[str, str | type(ErrorSchema)]]:
    """
    Generate error responses for FastAPI routes.

    :param errors: error response status code and description in a tuple
    :return: error responses
    """
    error_responses = {}
    for error in errors:
        error_response = _create_error_response(*error)
        error_responses.update(error_response)
    return error_responses


def _create_error_response(
    status_code: int,
    description: str,
) -> dict[int, dict[str, str | type(BaseSchema)]]:
    if status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        error_schema = ValidationInputErrorsSchema
    else:
        error_schema = ErrorSchema
    return {
        status_code: {
            "model": error_schema,
            "description": description,
        },
    }
