from exceptions.service.base import BaseServiceError


class PaginationError(BaseServiceError):
    detail = "Pagination error"


class PaginationServiceNotConfiguredError(PaginationError):
    detail = "Pagination service is not configured"
