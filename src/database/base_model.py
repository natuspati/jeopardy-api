from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import MetaData, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.sqltypes import NVARCHAR, TIMESTAMP, Integer, String

meta = MetaData()


class IDDBMixin:
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
    type_annotation_map = {
        int: Integer,
        datetime: TIMESTAMP(timezone=False),
        str: String().with_variant(NVARCHAR, "postgresql"),
    }


class BaseDBModel(Base):
    __abstract__ = True

    def to_dict(
        self,
        exclude: set[str] | None = None,
        include_related: bool = False,
        to_string: bool = False,
    ) -> dict[str, Any]:
        """
        Convert SQLAlchemy model instance to dictionary.

        :param exclude: set of columns to exclude
        :param include_related: whether to include related columns
        :param to_string: whether to convert to string
        :return: dictionary of model instance
        """
        exclude = exclude or set()

        if include_related:
            model_columns = inspect(self).mapper.attrs
        else:
            model_columns = inspect(self).mapper.column_attrs

        model_as_dict = {}
        for column in model_columns:
            self._add_column_key(
                model_as_dict=model_as_dict,
                column=column,
                to_string=to_string,
                exclude=exclude,
            )

        if exclude:
            for attribute in exclude:
                model_as_dict.pop(attribute, None)

        return model_as_dict

    def _add_column_key(
        self,
        model_as_dict: dict[str, Any],
        column,
        exclude: set,
        to_string: bool = False,
    ) -> None:
        column_key = column.key
        if column_key not in exclude:
            column_value = getattr(self, column_key)
            if isinstance(column_value, list):
                column_value = [model.to_dict() for model in column_value]
            elif isinstance(column_value, BaseDBModel):
                column_value = column_value.to_dict(to_string=to_string)
            elif to_string:
                column_value = self._convert_column_value(column_value)
            model_as_dict[column_key] = column_value

    @classmethod
    def _convert_column_value(cls, column_value: Any) -> str | int | float | None:
        match column_value:
            case int():
                converted_column_value = column_value
            case float():
                converted_column_value = column_value
            case datetime():
                converted_column_value = column_value.isoformat()
            case Enum():
                converted_column_value = column_value.value
            case None:
                return None
            case _:
                converted_column_value = str(column_value)
        return converted_column_value


class BaseDBModelWithID(BaseDBModel, IDDBMixin):
    __abstract__ = True
