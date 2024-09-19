from exceptions.http.base import BaseApiError


class DatabaseApiError(BaseApiError):
    detail = "Internal database error"


class DatabaseDataValidationApiError(DatabaseApiError):
    detail = "Database data validation error"
