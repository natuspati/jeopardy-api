from typing import Annotated

from fastapi import BackgroundTasks, Depends
from redis.asyncio import Redis

from api.schemas.base import BaseSchema
from cutom_types.base import FUNCTION_TYPE
from cutom_types.redis import REDIS_SETTABLE_TYPE, REDIS_VALUE_TYPE
from services.redis.dependencies import get_redis_client
from services.redis.utils import deserialize, make_key, serialize
from settings import settings


class RedisStoreService:
    _default_expiration = settings.redis_default_expiration_time
    _default_namespace = settings.redis_default_namespace
    _default_empty_value = settings.redis_empty_value

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        store_client: Annotated[Redis, Depends(get_redis_client)],
        expiration: int = _default_expiration,
        namespace: str = _default_namespace,
        empty_value: str = _default_empty_value,
    ) -> None:
        self._background_tasks = background_tasks
        self._store_client = store_client
        self._expiration = expiration
        self._namespace = namespace
        self._empty_value = empty_value

    async def get_entity(
        self,
        entity_key: bytes | str | memoryview,
        schema: type[BaseSchema] = None,
    ) -> REDIS_SETTABLE_TYPE | None:
        """
        Get saved object for a specific object key.

        :param entity_key: a key generated based on object args and kwargs
        :param schema: a schema used to deserialize object
        :return: saved entity
        """
        stored_entity = await self._get_entity(entity_key)
        if stored_entity and stored_entity != self._empty_value:
            return self._deserialize(stored_entity, schema)

    async def set_entity(
        self,
        entity_key: bytes | str | memoryview,
        value: REDIS_SETTABLE_TYPE,
        expire: int | None = None,
        override_existing: bool = True,
        update_existing: bool = False,
        get_existing: bool = False,
        keep_time_stamp: bool = False,
    ) -> REDIS_VALUE_TYPE | None:
        """
        Set an entity to storage.

        Entity will be stored with a key and has specified expiration time.

        :param entity_key: key name
        :param value: an object
        :param expire: expiration time
        :param override_existing: set entity if it does not exist
        :param update_existing: update entity if it exists, otherwise do not set entity
        :param get_existing: fetch object if it exists, otherwise return None
        :param keep_time_stamp: keep time stamp on entity if it exists
        :return: None or existing value
        """
        await self._set_entity(
            entity_key=entity_key,
            value=value,
            expire=expire,
            override_existing=override_existing,
            update_existing=update_existing,
            get_existing=get_existing,
            keep_time_stamp=keep_time_stamp,
        )

    async def background_set_entity(
        self,
        entity_key: bytes | str | memoryview,
        value: REDIS_SETTABLE_TYPE,
        expire: int | None = None,
        override_existing: bool = True,
        update_existing: bool = False,
        keep_time_stamp: bool = False,
    ) -> None:
        """
        Set an entity to storage in the background.

        Entity will be stored with a key and has specified expiration time.

        :param entity_key: key name
        :param value: an object
        :param expire: expiration time
        :param override_existing: set entity if it does not exist
        :param update_existing: update entity if it exists, otherwise do not set entity
        :param keep_time_stamp: keep time stamp on entity if it exists
        :return: None or existing value
        """
        await self._add_to_background(
            func=self._set_entity,
            entity_key=entity_key,
            value=value,
            expire=expire,
            override_existing=override_existing,
            update_existing=update_existing,
            get_existing=False,
            keep_time_stamp=keep_time_stamp,
        )

    async def set_entity_empty(
        self,
        entity_key: str,
        expire: int | None = None,
        get_existing: bool = False,
    ) -> REDIS_VALUE_TYPE | None:
        """
        Set an entity to storage with empty value.

        :param entity_key: key name
        :param expire: expiration time
        :param get_existing: fetch object if it exists, otherwise return None
        :return: None or existing value
        """
        return await self.set_entity(
            entity_key=entity_key,
            value=self._empty_value,
            expire=expire,
            get_existing=get_existing,
        )

    async def background_set_entity_empty(
        self,
        entity_key: str,
        expire: int | None = None,
    ) -> None:
        """
        Set an entity to storage with empty value in the background.

        :param entity_key: key name
        :param expire: expiration time
        :return: None or existing value
        """
        await self._add_to_background(
            self._set_entity,
            entity_key=entity_key,
            value=self._empty_value,
            expire=expire,
        )

    async def remove_entities(
        self, *entity_keys: bytes | str | memoryview, background: bool = False
    ) -> None:
        """
        Remove an object from storage.

        :param entity_keys: key names
        :param background: remove entities in the background
        :return:
        """
        if background:
            await self._add_to_background(
                self._store_client.delete,
                *entity_keys,
            )
        else:
            await self._store_client.delete(*entity_keys)

    async def get_or_set_entity(
        self,
        entity_key: bytes | str | memoryview,
        value: REDIS_VALUE_TYPE,
        expire: int | None = None,
        schema: BaseSchema = None,
    ) -> REDIS_VALUE_TYPE | None:
        """
        Get or set entity in storage.

        :param entity_key: entity key
        :param value: entity value
        :param expire: expiration time
        :param schema: a schema used to deserialize object
        :return: stored or saved value
        """
        stored_entity = await self.get_entity(entity_key, schema)
        if not stored_entity:
            self.set_entity(
                entity_key=entity_key,
                value=value,
                expire=expire,
            )
            stored_entity = self.get_entity(entity_key, schema)
        return stored_entity

    def make_entity_key(
        self,
        prefix: str,
        *args,
        namespace: str = None,
        **kwargs,
    ) -> str:
        """
        Make an object key that will be used as an identification for an object.

        :param prefix: prefix that will be added to object(s) key
        :param args: object(s) args for making a key
        :param namespace: namespace for making a key
        :param kwargs: object(s) kwargs for making a key
        :return: entity key
        """
        return make_key(
            namespace=namespace or self._namespace,
            prefix=prefix,
            args=args,
            kwargs=kwargs,
        )

    async def _get_entity(
        self,
        entity_key: bytes | str | memoryview,
    ) -> REDIS_VALUE_TYPE | None:
        return await self._store_client.get(entity_key)

    async def _set_entity(
        self,
        entity_key: bytes | str | memoryview,
        value: REDIS_SETTABLE_TYPE,
        expire: int | None = None,
        override_existing: bool = True,
        update_existing: bool = False,
        get_existing: bool = False,
        keep_time_stamp: bool = False,
    ) -> REDIS_VALUE_TYPE | None:
        return await self._store_client.set(
            name=entity_key,
            value=self._serialize(value),
            ex=expire or self._expiration,
            nx=not override_existing,
            xx=update_existing,
            get=get_existing,
            keepttl=keep_time_stamp,
        )

    async def _add_to_background(self, func: FUNCTION_TYPE, *args, **kwargs) -> None:
        self._background_tasks.add_task(func, *args, **kwargs)

    @classmethod
    def _serialize(cls, value: REDIS_SETTABLE_TYPE) -> REDIS_VALUE_TYPE:
        return serialize(value)

    @classmethod
    def _deserialize(
        cls,
        value: REDIS_VALUE_TYPE,
        schema: type[BaseSchema] = None,
    ) -> REDIS_SETTABLE_TYPE:
        return deserialize(value, schema)
