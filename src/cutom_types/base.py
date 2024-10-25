from typing import Any, Awaitable, Callable, TypeVar, Union

T = TypeVar("T")  # noqa: WPS111
FUNCTION_TYPE = Union[Callable[..., Any], Awaitable[Any]]
