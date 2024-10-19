from typing import Any

from exceptions.service.base import BaseServiceError


class QueryManagerError(BaseServiceError):
    detail = "Query manager module error"


class AssociationModelNotFoundError(QueryManagerError):
    detail = "Association model not found"


class UnsupportedWhereClauseError(QueryManagerError):
    def __init__(self, operator: str):
        detail = f"Unsupported where clause, operator: {operator}"
        super().__init__(detail)


class InvalidBetweenClauseError(QueryManagerError):
    def __init__(self, *bounds: Any):
        detail = f"Invalid BETWEEN clause, bounds: {bounds}"
        super().__init__(detail)


class InvalidInClauseError(QueryManagerError):
    def __init__(self, collection: Any):
        detail = f"Invalid IN clause, collection: {collection}"
        super().__init__(detail)
