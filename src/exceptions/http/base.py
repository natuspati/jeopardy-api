from abc import ABC

from fastapi import HTTPException, status

from exceptions.service.base import BaseServiceError


class BaseHTTPError(HTTPException, ABC):
    detail = "Description unavailable"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        detail: str | None = None,
        status_code: int | None = None,
    ):
        super().__init__(
            detail=detail or self.detail,
            status_code=status_code or self.status_code,
        )


class HTTPError(BaseHTTPError):
    def __init__(self, service_error: BaseServiceError):
        super().__init__(
            detail=service_error.detail,
            status_code=service_error.status_code,
        )


class InternalHTTPError(BaseHTTPError):
    def __init__(self, error: Exception):
        super().__init__(detail=str(error), status_code=self.status_code)
