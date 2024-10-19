import asyncio
import contextvars
from typing import Any, Callable, Coroutine

from api.context_variables import is_concurrent


async def run_concurrently(
    *coroutines: Coroutine,
) -> list[Any]:
    """
    Run coroutines concurrently.

    Custom context is set for the coroutines, with `is_concurrent` context variable
    set to True.

    :param coroutines: coroutines to run
    :return: list of coroutine results in the same order as coroutines
    """
    context = contextvars.copy_context()
    context.run(is_concurrent.set, True)  # noqa: WPS425

    tasks = []
    async with asyncio.TaskGroup() as tg:
        for coro in coroutines:
            task = tg.create_task(coro, context=context)
            tasks.append(task)
    return [comp_task.result() for comp_task in tasks]


def customize_openapi(  # noqa: WPS231, C901
    func: Callable[..., dict],
) -> Callable[..., dict]:
    """
    Customize OpenAPI schema.

    Removes default 422 responses from Pydantic validation dependencies.

    Add default 500 response to all routes.

    :param func: OpenAPI function
    :return: customised OpenAPI function
    """

    def wrapper(*args, **kwargs) -> dict:  # noqa: WPS231
        res = func(*args, **kwargs)
        for _, method_item in res["paths"].items():
            for _, param in method_item.items():
                responses = param["responses"]
                if "422" in responses:
                    content = responses["422"]["content"]  # noqa: WPS529
                    schema = content["application/json"]["schema"]  # noqa: WPS529
                    if schema["$ref"].endswith("HTTPValidationError"):
                        del responses["422"]  # noqa: WPS529
                if "500" not in responses:
                    responses["500"] = {
                        "description": "Internal Server Error",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorSchema"},
                            },
                        },
                    }
        return res

    return wrapper
