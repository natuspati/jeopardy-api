import asyncio
import contextvars
from typing import Any, Coroutine

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
