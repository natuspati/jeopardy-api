from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import (  # noqa: WPS235
    BinaryExpression,
    ColumnElement,
    Delete,
    Insert,
    Label,
    Select,
    Update,
    asc,
    delete,
    desc,
    func,
    insert,
    select,
    update,
)
from sqlalchemy.orm import InstrumentedAttribute, selectinload
from sqlalchemy.sql.dml import ReturningDelete, ReturningInsert, ReturningUpdate

from cutom_types.database import ASSOCIATION_MODEL_TYPE
from database.base_model import BaseDBModel
from exceptions.module.query_manager import (
    AssociationModelNotFoundError,
    InvalidBetweenClauseError,
    InvalidInClauseError,
    UnsupportedWhereClauseError,
)


class BaseQueryManager(ABC):
    """
    Base query manager for database models.

    `_model` specifies default model to apply SQL operations.
    `_association_models` specifies models with foreign key relationships to model.

    Example definition of `_association_models`:

    .. code-block:: python

        _association_models = {
        "address": {
            "model": AddressModel,
            "on": UserModel.address_id == AddressModel.id,
            "isouter": False
        }
    """

    _model: type[BaseDBModel] = BaseDBModel
    _association_models: ASSOCIATION_MODEL_TYPE = {}

    @classmethod
    def select(  # noqa: C901
        cls,
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
    ) -> Select:
        """
        Select query for a model.

        :param model: database model
        :param columns: columns to select
        :param where: where conditions
        :param order: order conditions
        :param limit: limit number of columns
        :param offset: offset in results
        :param join: join conditions
        :param related: columns that have relationship woth other tables
        :param group_by: list of columns for grouping
        :param having: having conditions
        :param distinct: whether to select distinct values
        :return: select query
        """
        model = model or cls._model

        query = select(*columns) if columns else select(model)

        if distinct:
            query = cls.distinct(query)

        if join:
            query = cls.join(query, join)

        if related:
            query = cls.select_related(
                query,
                model=model,
                related_column_names=related,
            )

        if where:
            query = cls.where(query, model=model, **where)

        if group_by:
            query = cls.group_by(query, group_by)

        if having:
            query = cls.having(query, model, **having)

        if order:
            query = cls.order(query, model=model, **order)

        if limit is not None:
            query = cls.limit(query, limit)

        if offset is not None:
            query = cls.offset(query, offset)

        return query

    @classmethod
    def insert(
        cls,
        model: type[BaseDBModel] | None = None,
        returning: bool = True,
        **values: Any,
    ) -> Insert | ReturningInsert:
        """
        Insert query for a model.

        :param model: database model
        :param returning: return insert query
        :return: insert query
        """
        model = model or cls._model
        query = insert(model)
        if values:
            query = cls.values(query, **values)
        if returning:
            return cls.returning(query, model=model)
        return query

    @classmethod
    def update(
        cls,
        where: dict[str, Any],
        returning: bool = True,
        model: type[BaseDBModel] | None = None,
        **values: Any,
    ) -> Update:
        """
        Update query for a model.

        :param where: where conditions
        :param returning: whether to return
        :param model: database model
        :param values: values to update with
        :return: update query
        """
        model = model or cls._model
        query = update(model)
        if values:
            query = cls.values(query, **values)
            query = cls.where(query, model=model, **where)
        if returning:
            query = cls.returning(query, model=model)
        return query

    @classmethod
    def delete(
        cls,
        where_clauses: dict[str, Any],
        model: type[BaseDBModel] | None = None,
    ) -> Delete:
        """
        Delete query for a model.

        :param where_clauses: where_clauses
        :param model: database model
        :return: delete query
        """
        model = model or cls._model
        query = delete(model)
        return cls.where(query, model=model, **where_clauses)

    @classmethod
    def total_count(cls, model: type[BaseDBModel] | None = None) -> Select:
        """
        Count query for a model.

        :param model: database model
        :return: select query for total count
        """
        model = model or cls._model
        return select(func.count()).select_from(model)

    @classmethod
    def where(
        cls,
        query: Select | Update | Delete,
        model: type[BaseDBModel] = _model,
        **where_clauses: tuple[str, Any] | Any,
    ) -> Select | Delete:
        """
        Apply where conditions to SQL Alchemy query.

        :param query: select, update or delete query
        :param model: database model
        :param where_clauses: where conditions
        :return: query with where conditions applied
        """
        conditions = []
        for field, clause in where_clauses.items():
            condition = cls._create_where_clause(
                column=getattr(model, field),
                clause=clause,
            )
            if condition is not None:
                conditions.append(condition)
        return query.where(*conditions) if conditions else query

    @classmethod
    def order(
        cls,
        query: Select,
        model: type[BaseDBModel] = _model,
        **order_clauses: str,
    ) -> Select:
        """
        Apply order conditions to select query.

        :param query: select query
        :param model: database model
        :param order_clauses: order conditions
        :return: query with order conditions applied
        """
        for field, order_type in order_clauses.items():
            order_column = getattr(model, field)
            if order_type == "asc":
                query = query.order_by(asc(order_column))
            elif order_type == "desc":
                query = query.order_by(desc(order_column))
        return query

    @classmethod
    def offset(cls, query: Select, offset: int) -> Select:
        """
        Apply offset to select query.

        :param query: select query
        :param offset: offset for the results
        :return: query with offset applied
        """
        return query.offset(offset)

    @classmethod
    def join(
        cls,
        query: Select,
        joins: list[ASSOCIATION_MODEL_TYPE],
    ) -> Select:
        """
        Apply join conditions to select query.

        :param query: select query
        :param joins: join conditions
        :return: select query with join conditions applied
        """
        related_models = []
        for join in joins:
            related_model, on_clause, isouter = cls._join_details(join)
            aliased_columns = cls._alias_columns(related_model)
            query = query.add_columns(*aliased_columns)
            query = query.join(related_model, on_clause, isouter=isouter)
            related_models.append(related_model)
        return query

    @classmethod
    def select_related(
        cls,
        query: Select,
        related_column_names: list[str],
        model: type[BaseDBModel],
    ) -> Select:
        """
        Select related columns from tables that have relationships with a given table.

        :param query: select query
        :param related_column_names: list of column names that link to related tables
        :param model: database model
        :return: select query with related columns that are populated
        """
        options = []
        for column_name in related_column_names:
            related_column: InstrumentedAttribute = getattr(model, column_name)
            options.append(selectinload(related_column))
        return query.options(*options)

    @classmethod
    def group_by(cls, query: Select, group_by: list[Any]) -> Select:
        """
        Apply group by conditions to select query.

        :param query: select query
        :param group_by: list of columns for grouping
        :return: query with group by conditions applied
        """
        return query.group_by(*group_by)

    @classmethod
    def having(
        cls,
        query: Select,
        model: type[BaseDBModel] = _model,
        **having_clauses: Any,
    ) -> Select:
        """
        Apply having conditions to select query.

        :param query: select query
        :param model: database model
        :param having_clauses: having clauses
        :return: query with having conditions applied
        """
        conditions = [
            getattr(model, field) == value for field, value in having_clauses.items()
        ]
        return query.having(*conditions) if conditions else query

    @classmethod
    def limit(cls, query: Select, limit: int) -> Select:
        """
        Apply limit to select query.

        :param query: select query
        :param limit: limit for the number of results
        :return: query with limit applied
        """
        return query.limit(limit)

    @classmethod
    def distinct(cls, query: Select) -> Select:
        """
        Apply distinct to select query.

        :param query: select query
        :return: query with distinct applied
        """
        return query.distinct()

    @classmethod
    def values(cls, query: Insert | Update, **values: Any) -> Insert | Update:
        """
        Add values to insert or update query.

        :param query: insert or update query
        :param values: values
        :return: insert or update query with mapped values
        """
        return query.values(**values)

    @classmethod
    def returning(
        cls,
        query: Insert | Delete | Update,
        model: type[BaseDBModel] = _model,
    ) -> ReturningInsert | ReturningUpdate | ReturningDelete:
        """
        Add returning conditions to insert, update or delete query.

        :param query: insert, update, delete query
        :param model: database model
        :return: returning query
        """
        return query.returning(model)

    @classmethod
    def _join_details(
        cls,
        join: ASSOCIATION_MODEL_TYPE,
    ) -> tuple[type[BaseDBModel], ColumnElement, bool]:
        """
        Get join details based on the join specification.

        :param join: join specification
        :return: related model, on clause, and isouter flag
        """
        if isinstance(join, str):
            assoc = cls._association_models.get(join)
            if not assoc:
                raise AssociationModelNotFoundError()
            return assoc["model"], assoc["on"], assoc.get("isouter", False)

        return join["model"], join["on"], join.get("isouter", False)

    @classmethod
    def _create_where_clause(
        cls,
        column: InstrumentedAttribute,
        clause: tuple[str | Any] | Any,
    ) -> ColumnElement | BinaryExpression | None:
        if isinstance(clause, tuple) and len(clause) == 2:
            operator, value = clause
            return cls._match_where_clause(
                column=column,
                operator=operator,
                value=value,
            )
        return column == clause

    @classmethod
    def _match_where_clause(  # noqa: WPS212
        cls,
        column: InstrumentedAttribute,
        operator: str,
        value: Any,
    ) -> ColumnElement | BinaryExpression | None:
        match operator:
            case "eq":
                return column == value
            case "ne":
                return column != value
            case "lt":
                return column < value
            case "le":
                return column <= value
            case "gt":
                return column > value
            case "ge":
                return column >= value
            case "between":
                return cls._create_between_clause(
                    column=column,
                    bounds=value,
                )
            case "not_between":
                return cls._create_between_clause(
                    column=column,
                    bounds=value,
                    negative=True,
                )
            case "in":
                return cls._create_in_clause(
                    column=column,
                    collection=value,
                )
            case "not_in":
                return cls._create_in_clause(
                    column=column,
                    collection=value,
                    negative=True,
                )
            case "is_not":
                return column.isnot(value)
            case "ilike":
                return column.ilike(value)
            case "not_ilike":
                return column.notilike(value)
            case "like":
                return column.like(value)
            case "not_like":
                return column.not_like(value)
            case "contains":
                return column.contains(value)
            case _:
                raise UnsupportedWhereClauseError(operator)

    @classmethod
    def _create_between_clause(  # noqa: WPS231
        cls,
        column: InstrumentedAttribute,
        bounds: tuple[Any, Any],
        negative: bool = False,
    ) -> BinaryExpression | None:
        if not isinstance(bounds, tuple) or len(bounds) != 2:
            raise InvalidBetweenClauseError(bounds)

        lower, upper = bounds

        if lower is None and upper is None:
            return None
        if lower is None:
            between_clause = column <= upper
        elif upper is None:
            between_clause = column >= lower
        elif lower < upper:
            between_clause = column.between(lower, upper)
        else:
            raise InvalidBetweenClauseError(bounds)

        return ~between_clause if negative else between_clause

    @classmethod
    def _create_in_clause(
        cls,
        column: InstrumentedAttribute,
        collection: list | tuple | set,
        negative: bool = False,
    ) -> BinaryExpression:
        if isinstance(collection, (list, tuple, set)):
            in_clause = column.in_(collection)
            return ~in_clause if negative else in_clause
        raise InvalidInClauseError(collection)

    @classmethod
    def _alias_columns(cls, model: type[BaseDBModel]) -> list[Label]:
        model_name = model.__tablename__
        column_labels = []
        for col in model.__table__.columns:
            label = col.label(f"{model_name}_{col.name}")
            column_labels.append(label)
        return column_labels

    @property
    @abstractmethod
    def _model(self) -> type[BaseDBModel]:
        pass
