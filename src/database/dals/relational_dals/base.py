import contextvars
import logging
from abc import ABC, abstractmethod
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import Executable
from sqlalchemy.exc import (
    DataError,
    DBAPIError,
    IntegrityError,
    ProgrammingError,
    ResourceClosedError,
)
from sqlalchemy.ext.asyncio import AsyncSession

from api.context_variables import is_concurrent
from database.base_model import BaseDBModel
from database.dependencies import get_db_manager, get_db_session
from database.manager import DatabaseConnectionManager
from database.manager import db_manager as default_db_manager
from database.query_managers.base import BaseQueryManager
from exceptions.module.database import DatabaseDetailError

logger = logging.getLogger(__name__)

common_db_exceptions = (
    ProgrammingError,
    ResourceClosedError,
    IntegrityError,
    DataError,
    DBAPIError,
)

DB_MANAGER_ANNOTATION = Annotated[DatabaseConnectionManager, Depends(get_db_manager)]


class BaseDAL(ABC):  # noqa: WPS338
    @property
    @abstractmethod
    def _qm(self) -> BaseQueryManager:
        """Query manager for database access layer."""
        pass

    def __init__(
        self,
        db_session: Annotated[AsyncSession, Depends(get_db_session)],
        db_manager: DB_MANAGER_ANNOTATION = default_db_manager,
    ):
        self._db_session = db_session
        self._db_manager = db_manager

    async def select(
        self,
        many: bool = False,
        model: type[BaseDBModel] | None = None,
        columns: list[Any] | None = None,
        where: dict[str, Any] | None = None,
        order: dict[str, str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        join: list[str | dict[str, Any]] | None = None,
        related: list[str] | None = None,
        group_by: list[Any] | None = None,
        having: dict[str, Any] | None = None,
        distinct: bool = False,
    ):
        """
        Select rows for a table.

        :param many: select many rows
        :param model: database model
        :param columns: columns to select
        :param where: where conditions
        :param order: order conditions
        :param limit: limit number of columns
        :param offset: offset in results
        :param join: join conditions
        :param related: columns that have relationship with other tables
        :param group_by: list of columns for grouping
        :param having: having conditions
        :param distinct: whether to select distinct values
        :return: select query
        """
        query = self._qm.select(
            model=model,
            columns=columns,
            where=where,
            order=order,
            limit=limit,
            offset=offset,
            join=join,
            related=related,
            group_by=group_by,
            having=having,
            distinct=distinct,
        )

        if many:
            return await self._scalars(query)
        return await self._scalar(query)

    async def insert(
        self,
        model: type[BaseDBModel] | None = None,
        returning: bool = True,
        **values: Any,
    ):
        """
        Insert a row to a table.

        :param model: database model
        :param returning: return insert query
        :return: insert query
        """
        query = self._qm.insert(
            model=model,
            returning=returning,
            **values,
        )
        if returning:
            return await self._scalar(query)
        await self._execute(query)

    async def update(
        self,
        where: dict[str, Any],
        model: type[BaseDBModel] | None = None,
        returning: bool = True,
        **values: Any,
    ):
        """
        Update a row in a table.

        :param where: where clause
        :param model: database model
        :param returning: whether to return update row
        :param values: values to update in the row
        :return: updated row or None
        """
        query = self._qm.update(
            where=where,
            returning=returning,
            model=model,
            **values,
        )
        if returning:
            return await self._scalar(query)
        await self._execute(query)

    async def delete(
        self,
        model: type[BaseDBModel] | None = None,
        **where_clauses: Any,
    ) -> None:
        """
        Delete a row in a table.

        :param model: database model
        :param where_clauses: where clauses
        :return: None
        """
        query = self._qm.delete(
            where_clauses=where_clauses,
            model=model,
        )
        await self._execute(query)

    async def total_count(
        self,
        model: type[BaseDBModel] | None = None,
    ) -> int:
        """
        Count all rows in a table.

        :param model: database model
        :return: number of rows
        """
        query = self._qm.total_count(model)
        return await self._scalar(query)

    async def commit(self) -> None:
        """
        Commit changes to database.

        :return:
        """
        await self._db_session.commit()

    async def _execute(self, query: Executable):
        """
        Execute SQL query..

        :param query: SQLAlchemy Core statement
        :return: SQLAlchemy result
        """
        concurrent = self._get_concurrency_status()

        if concurrent:
            try:
                async with self._db_manager.session() as session:
                    result = await session.execute(query)
            except common_db_exceptions as error:
                self._handle_error(error, str(error))
            else:
                return result
        else:
            try:
                return await self._db_session.execute(query)
            except common_db_exceptions as error:  # noqa: WPS440
                self._handle_error(error, str(query))

    async def _scalar(self, query: Executable):
        """
        Execute SQL query that returns a single row and apply scalar.

        The scalar result is transformed to SQLAlchemy model instance.

        The method should be used to execute statements that return a single row.

        :param query: SQLAlchemy Core statement
        :return: SQLAlchemy model instance
        """
        concurrent = self._get_concurrency_status()

        if concurrent:
            try:
                async with self._db_manager.session() as session:
                    result = await session.scalar(query)
            except common_db_exceptions as error:
                self._handle_error(error, str(query))
            else:
                return result
        else:
            try:
                return await self._db_session.scalar(query)
            except common_db_exceptions as error:  # noqa: WPS440
                self._handle_error(error, str(query))

    async def _scalars(self, query: Executable):
        """
        Execute SQL query that returns several rows and applies scalar.

        The scalar results is transformed to list of SQLAlchemy model instances.

        The method should be used to execute statements that return a list of rows.

        :param query: SQLAlchemy Core statement
        :return: list of SQLAlchemy model instances
        """
        concurrent = self._get_concurrency_status()

        if concurrent:
            try:
                async with self._db_manager.session() as session:
                    scalar_result = await session.scalars(query)
            except common_db_exceptions as error:
                self._handle_error(error, str(query))
            else:
                return scalar_result.all()
        else:
            try:
                scalar_result = await self._db_session.scalars(query)
            except common_db_exceptions as error:  # noqa: WPS440
                self._handle_error(error, str(query))
            else:
                return scalar_result.all()

    @classmethod
    def _get_concurrency_status(cls) -> bool:
        ctxt = contextvars.copy_context()
        return ctxt.get(is_concurrent, False)

    @classmethod
    def _handle_error(cls, error: Exception, statement: str) -> None:
        logger.error(
            "Database error, statement: {0},\ntype: {1},\nmessage: {2}".format(
                statement,
                type(error),
                error,
            ),
        )
        raise DatabaseDetailError(error)
