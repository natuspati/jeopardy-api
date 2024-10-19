import logging

from sqlalchemy import Delete, Insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.dals.relational_dals.base import common_db_exceptions
from database.manager import default_db_manager
from database.migrations.data.queries import ORDERED_QUERIES
from exceptions.service.database import DatabaseDetailError

logger = logging.getLogger(__name__)


async def run_data_migrations(direction: bool) -> None:
    async with default_db_manager.session() as session:
        await _run_queries(session=session, direction=direction)
    logger.info("Successfully run data migrations.")


async def _run_queries(
    session: AsyncSession,
    direction: bool,
) -> None:
    create_queries, delete_queries = _get_queries_in_each_direction()
    if direction:
        for delete_query in delete_queries:
            await _run_query(session, delete_query)
        for create_query in create_queries:
            await _run_query(session, create_query)
    else:
        for delete_query in delete_queries:  # noqa: WPS440
            await _run_query(session, delete_query)


async def _run_query(session: AsyncSession, query: Insert | Delete) -> None:
    try:
        await session.execute(query)
    except common_db_exceptions as error:
        raise DatabaseDetailError(error)


def _get_queries_in_each_direction() -> tuple[list[Insert], list[Delete]]:
    ordered_create_queries, ordered_delete_queries = [], []
    for create_queries, delete_queries in ORDERED_QUERIES:
        ordered_create_queries.extend(create_queries)
        ordered_delete_queries.extend(delete_queries)
    ordered_delete_queries.reverse()
    return ordered_create_queries, ordered_delete_queries
