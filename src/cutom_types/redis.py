from typing import Any, Sequence

from api.schemas.base import BaseSchema

REDIS_SINGLE_VALUE_TYPE = str | int | float
REDIS_VALUE_TYPE = bytes | memoryview | REDIS_SINGLE_VALUE_TYPE
REDIS_SETTABLE_TYPE = REDIS_SINGLE_VALUE_TYPE | BaseSchema | Sequence | dict[str, Any]
