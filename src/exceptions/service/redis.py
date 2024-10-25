from exceptions.service.base import BaseServiceError


class RedisError(BaseServiceError):
    detail = "Redis error"


class RedisConnectionError(RedisError):
    detail = "Redis connection error"
