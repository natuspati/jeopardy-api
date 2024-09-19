from exceptions.module.base import BaseModuleError


class PaginationError(BaseModuleError):
    detail = "Pagination error"


class PaginationServiceNotConfiguredError(PaginationError):
    detail = "Pagination service is not configured"
