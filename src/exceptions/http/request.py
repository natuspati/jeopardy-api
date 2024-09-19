from fastapi import status
from fastapi.exceptions import RequestValidationError

from exceptions.http.base import BaseApiError


class RequestValidationApiError(BaseApiError):
    detail = "Request validation error"
    status_code = status.HTTP_400_BAD_REQUEST


class DetailedRequestValidationApiError(RequestValidationApiError):
    def __init__(self, validation_error: RequestValidationError):
        detail = f"Validation errors: {validation_error}"
        super().__init__(detail)


class InvalidQueryParamsApiError(BaseApiError):
    detail = "Invalid query parameters error"
    status_code = status.HTTP_400_BAD_REQUEST


class DateTimeQueryParamsApiError(InvalidQueryParamsApiError):
    detail = "Invalid start and end dates in query parameters"


class OrderQueryParamsApiError(InvalidQueryParamsApiError):
    detail = "Invalid order in query parameters"
