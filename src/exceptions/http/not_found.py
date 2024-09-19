from fastapi import status

from exceptions.http.base import BaseApiError


class NotFoundApiError(BaseApiError):
    detail = "Resource not found."
    status_code = status.HTTP_404_NOT_FOUND
