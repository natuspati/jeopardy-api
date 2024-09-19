from datetime import datetime
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

    def to_dict(self, exclude: set[str] | None = None) -> dict[str, Any]:
        """
        Convert SQLAlchemy model instance to dictionary.

        :param exclude: set of columns to exclude
        :return: dictionary of model instance
        """
        model_as_dict = {
            column.key: getattr(self, column.key)
            for column in inspect(self).mapper.column_attrs
        }  # noqa: WPS221

        if exclude:
            for attribute in exclude:
                model_as_dict.pop(attribute, None)

        return model_as_dict


class BaseDBModelWithID(BaseDBModel, IDDBMixin):
    __abstract__ = True
