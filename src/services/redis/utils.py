import hashlib
from typing import Any, Literal, Sequence

from fastapi.types import IncEx
from orjson import JSONDecodeError, JSONEncodeError, orjson
from pydantic import ValidationError
from pydantic_core import PydanticSerializationError

from api.schemas.base import BaseSchema
from cutom_types.redis import (
    REDIS_SETTABLE_TYPE,
    REDIS_SINGLE_VALUE_TYPE,
    REDIS_VALUE_TYPE,
)
from exceptions.service.schema import SchemaValidationError
from exceptions.service.serialization import (
    JSONDecoderError,
    JSONEncoderError,
    NonSerializableError,
)
from settings import settings


def make_key(
    namespace: str = "",
    prefix: str = "",
    exclude_self: bool = False,
    *,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    """
    Make cache key based on md5 algorithm.

    :param namespace: entity_key prefix
    :param prefix: entity_key prefix
    :param exclude_self: if True, exclude first argument (self)
    :param args: function args
    :param kwargs: function kwargs
    :return: hashed key
    """
    if exclude_self:
        args = args[1:]

    key_string = f"{args}:{kwargs}".encode()
    entity_key = hashlib.md5(key_string, usedforsecurity=False)
    return f"{namespace}:{prefix}:{entity_key.hexdigest()}"


def dump_pydantic_schema(  # noqa: WPS211
    obj: BaseSchema,
    mode: Literal["json", "python"] = "json",
    include: IncEx = None,
    exclude: IncEx = None,
    context: dict[str, Any] = None,
    by_alias: bool = False,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
) -> dict[str, Any]:
    """
    Get dictionary representation of pydantic model.

    :param obj: pydantic model instance
    :param mode: json or python serialization mode
    :param include: set of fields to include in the output
    :param exclude: set of fields to exclude from the output
    :param context: additional context to pass to the serializer
    :param by_alias: whether to use the field's alias in the dictionary key if defined
    :param exclude_unset: whether to exclude fields that have not been explicitly set
    :param exclude_defaults: whether to exclude fields that are set to default value
    :param exclude_none: whether to exclude fields that have a value of `None`
    :raises NonSerializableError: if model is not convertible to dictionary
    :return: serialized pydantic model
    """
    try:
        return obj.model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
    except PydanticSerializationError as serialization_error:
        raise NonSerializableError() from serialization_error


def validate_to_pydantic_schema(
    obj: dict,
    schema: type[BaseSchema],
    strict: bool = None,
    from_attributes: bool = None,
    context: dict[str, Any] = None,
) -> BaseSchema:
    """
    Validate object with pydantic model.

    :param obj: object to validate
    :param schema: pydantic model
    :param strict: whether to enforce strict types
    :param from_attributes: whether to extract data from object attributes
    :param context: additional context to pass to the validator
    :raises SchemaValidationError: if object can not be validated
    :return: pydantic model instance
    """
    try:
        return schema.model_validate(
            obj=obj,
            strict=strict,
            from_attributes=from_attributes,
            context=context,
        )
    except ValidationError:
        raise SchemaValidationError()


def validate_to_pydantic_schemas(values: Sequence, schema: type[BaseSchema]) -> list:
    """
    Validate sequence of objects to pydantic model.

    Validation occurs if an object is dictionary.

    :param values: sequence of objects
    :param schema: pydantic model
    :return: list of validated pydantic model instances
    """
    items = []
    for item in values:
        if isinstance(item, dict):
            item = validate_to_pydantic_schema(item, schema)
        items.append(item)
    return items


def serialize(
    value: REDIS_SETTABLE_TYPE,
) -> REDIS_VALUE_TYPE:
    """
    Serialize value.

    Value is serialized to bytes by default.

    If value is a pydantic model, it is converted to dictionary.

    If a value is a sequence, pydantic models inside are converted to dictionary.

    :param value: value to serialize
    :raises JSONEncoderError: if value can not be encoded
    :return: serialized value
    """
    if isinstance(value, REDIS_SINGLE_VALUE_TYPE):
        return value

    if isinstance(value, BaseSchema):
        value = dump_pydantic_schema(value)
    elif isinstance(value, Sequence):
        value = [
            dump_pydantic_schema(item) if isinstance(item, BaseSchema) else item
            for item in value
        ]

    try:
        return orjson.dumps(value)
    except JSONEncodeError as json_error:
        raise JSONEncoderError(value) from json_error


def deserialize(  # noqa: C901
    value: REDIS_VALUE_TYPE,
    schema: type[BaseSchema] = None,
) -> REDIS_SETTABLE_TYPE:
    """
    Deserialize value.

    If pydantic model is provided, objects within decoded objected are validated.

    :param value: value to deserialize
    :param schema: pydantic model
    :raises JSONDecoderError: if value can not be decoded
    :return: deserialized value
    """
    if isinstance(value, REDIS_SINGLE_VALUE_TYPE):
        return value

    try:
        deserialized_value = orjson.loads(value)
    except JSONDecodeError as json_error:
        try:  # noqa: WPS505
            deserialized_value = value.decode(settings.redis_encoding)
        except UnicodeDecodeError:
            raise JSONDecoderError(value) from json_error

    if isinstance(deserialized_value, dict) and schema:
        deserialized_value = validate_to_pydantic_schema(deserialized_value, schema)
    elif isinstance(deserialized_value, Sequence) and schema:
        deserialized_value = validate_to_pydantic_schemas(deserialized_value, schema)

    return deserialized_value
