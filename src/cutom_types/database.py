from typing import Literal

from sqlalchemy import ColumnElement

from database.base_model import BaseDBModel

ISOLATION_LEVEL_TYPE = Literal[
    "SERIALIZABLE",
    "REPEATABLE READ",
    "READ COMMITTED",
    "READ UNCOMMITTED",
    "AUTOCOMMIT",
]

ASSOCIATION_MODEL_TYPE = dict[
    str,
    dict[str, type[BaseDBModel] | ColumnElement | bool],
]
