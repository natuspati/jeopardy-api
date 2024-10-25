from typing import Annotated

from fastapi import Depends

from services.redis.redis_store import RedisStoreService


class DataStoreInterface:
    def __init__(self, store_service: Annotated[RedisStoreService, Depends()]):
        self._store = store_service
