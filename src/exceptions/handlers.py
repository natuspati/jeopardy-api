from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse

from api.schemas.error import ErrorSchema, ValidationInputErrorsSchema
from exceptions.http.base import BaseHTTPError, HTTPError, InternalHTTPError
from exceptions.service.base import BaseServiceError


def add_exception_handlers(app: FastAPI) -> None:
    """
    Add exception handlers to FastAPI application.

    :param app: FastAPI application
    :return:
    """
    app.add_exception_handler(Exception, default_error_handler)
    app.add_exception_handler(BaseServiceError, service_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)


async def default_error_handler(request: Request, error: Exception) -> ORJSONResponse:
    """
    Handle all exceptions not inherited from `BaseServiceError`.

    :param request: request
    :param error: exception
    :return: internal service error response
    """
    return _format_error_json_response(InternalHTTPError(error))


async def service_error_handler(
    request: Request,
    error: BaseServiceError,
) -> ORJSONResponse:
    """
    Handle exceptions from `BaseServiceError` for REST and Websocket endpoints.

    Create response with status code from the error.

    :param request: request
    :param error: service error with status code
    :return: internal service error response
    """
    return _format_error_json_response(HTTPError(error))


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
    validation_errors = ValidationInputErrorsSchema(errors=error.args[0])
    return ORJSONResponse(
        content=validation_errors.model_dump(),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


def _format_error_json_response(error: BaseHTTPError) -> ORJSONResponse:
    return ORJSONResponse(
        content=ErrorSchema(detail=error.detail).model_dump(),
        status_code=error.status_code,
    )
