from abc import ABC

from fastapi import HTTPException, status

from exceptions.module.base import BaseModuleError


class BaseHTTPError(HTTPException, ABC):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Description unavailable"

    def __init__(
        self,
        detail: str | None = None,
        status_code: int | None = None,
    ):
        super().__init__(
            detail=detail or self.detail,
            status_code=status_code or self.status_code,
        )


class BaseApiError(BaseHTTPError):
    pass


class InternalApiError(BaseApiError):
    detail = "Internal server error"


class DetailedInternalApiError(InternalApiError):
    def __init__(self, module_error: BaseModuleError):
        detail = f"Internal server error: {module_error.detail}"
        super().__init__(detail)


class DetailedUncaughtApiError(BaseApiError):
    def __init__(self, error: Exception):
        detail = f"Uncaught exception: {error}"
        super().__init__(detail)
