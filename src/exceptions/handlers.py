from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse

from api.enums.app_state import AppEnvironmentEnum
from exceptions.http.base import (
    BaseHTTPError,
    DetailedInternalApiError,
    DetailedUncaughtApiError,
    InternalApiError,
)
from exceptions.http.request import (
    DetailedRequestValidationApiError,
    RequestValidationApiError,
)
from exceptions.module.base import BaseModuleError
from settings import settings


def add_exception_handlers(app: FastAPI) -> None:
    """
    Add exception handlers to FastAPI application.

    :param app: FastAPI application
    :return:
    """
    app.add_exception_handler(Exception, default_error_handler)
    app.add_exception_handler(BaseModuleError, module_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)


async def default_error_handler(request: Request, error: Exception) -> ORJSONResponse:
    """
    Handle all exceptions not inherited from `BaseModuleError`.

    If application run in production environment, error details are not returned.

    :param request: request
    :param error: exception
    :return: internal service error response
    """
    if settings.app_environment is AppEnvironmentEnum.prod:
        http_error = InternalApiError()
    else:
        http_error = DetailedUncaughtApiError(error)
    return _format_error_json_response(http_error)


async def module_error_handler(
    request: Request,
    error: BaseModuleError,
) -> ORJSONResponse:
    """
    Handle exceptions inherited from `BaseModuleError`.

    If application run in production environment, error details are not returned.

    :param request: request
    :param error: exception
    :return: internal service error response
    """
    if settings.app_environment is AppEnvironmentEnum.prod:
        http_error = InternalApiError()
    else:
        http_error = DetailedInternalApiError(error)
    return _format_error_json_response(http_error)


async def validation_error_handler(
    request: Request,
    error: RequestValidationError,
) -> ORJSONResponse:
    """
    Handle exceptions raised during input validation.

    :param request: request
    :param error: request validation error
    :return: bad request error response
    """
    if settings.app_environment is AppEnvironmentEnum.prod:
        http_error = RequestValidationApiError()
    else:
        http_error = DetailedRequestValidationApiError(error)
    return _format_error_json_response(http_error)


def _format_error_json_response(error: BaseHTTPError) -> ORJSONResponse:
    return ORJSONResponse(
        content={"detail": error.detail},
        status_code=error.status_code,
    )
