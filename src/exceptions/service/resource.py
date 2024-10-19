from fastapi import status

from exceptions.service.base import BaseServiceError


class ResourceExistsError(BaseServiceError):
    detail = "Resource exists error"
    status_code = status.HTTP_409_CONFLICT


class UserExistsError(ResourceExistsError):
    detail = "User already exists"


class PlayerExistsError(ResourceExistsError):
    detail = "Player already exists"
