from fastapi import status

from exceptions.service.base import BaseServiceError


class RequestError(BaseServiceError):
    detail = "Request validation error"
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidQueryParamsError(RequestError):
    detail = "Invalid query parameters error"


class DateTimeQueryParamsError(InvalidQueryParamsError):
    detail = "Invalid start and end dates in query parameters"


class OrderQueryParamsError(InvalidQueryParamsError):
    detail = "Invalid order in query parameters"
