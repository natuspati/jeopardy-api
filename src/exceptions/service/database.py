from exceptions.service.base import BaseServiceError


class DatabaseError(BaseServiceError):
    detail = "Database error"


class DatabaseDetailError(DatabaseError):
    def __init__(self, error: Exception):
        detail = f"Database error: type {type(error)}\nmessage: {error}"
        super().__init__(detail)


class DatabaseSessionManagerNotInitializedError(DatabaseError):
    detail = "Database session manager not initialized"
