from typing import AsyncGenerator

from fastapi import Depends
from redis.asyncio.client import Redis
from redis.exceptions import RedisError

from cutom_types.redis import REDIS_VALUE_TYPE
from exceptions.service.redis import RedisConnectionError
from src.settings import settings


class FakeRedis:
    def __init__(self):
        self._data = {}

    async def get(self, name: str) -> REDIS_VALUE_TYPE | None:
        """Get from the redis database, dummy."""
        return self._data.get(name)

    async def set(self, name: str, value: REDIS_VALUE_TYPE, **kwargs) -> None:
        """Set to the redis database, dummy."""
        self._data[name] = value

    async def delete(self, *names: str) -> None:
        """Delete from the redis database, dummy."""
        for name in names:
            self._data.pop(name)

    @classmethod
    async def ping(cls) -> bool:
        """Ping the redis database, dummy."""
        return True

    @classmethod
    async def aclose(cls) -> None:
        """Close the redis database, dummy."""
        pass


async def _get_redis_client() -> AsyncGenerator[Redis, None]:
    """
    Get redis client as an iterator.

    :raises RedisConnectionError: If redis client is not available
    :return: redis client
    """
    try:
        redis_client = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            socket_timeout=settings.redis_socket_timeout,
            encoding=settings.redis_encoding,
        )
    except RedisError as redis_error:
        raise RedisConnectionError() from redis_error

    response = await redis_client.ping()
    if not response:
        raise RedisConnectionError()
    try:
        yield redis_client
    finally:
        await redis_client.aclose()


async def get_redis_client(redis: Redis = Depends(_get_redis_client)) -> Redis:
    """Get redis client."""
    return redis


async def get_fake_redis_client() -> FakeRedis:
    """Get fake redis client, dummy."""
    return FakeRedis()
