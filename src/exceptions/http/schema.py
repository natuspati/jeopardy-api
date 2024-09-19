from fastapi import status

from exceptions.http.base import BaseApiError


class BaseSchemaApiError(BaseApiError):
    detail = "Schema error"


class AllFieldsUnsetValidationApiError(BaseSchemaApiError):
    detail = "At least one field must be set"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
