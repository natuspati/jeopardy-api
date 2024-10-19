from fastapi import Request

from api.schemas.base import BaseSchema
from api.schemas.pagination import PaginatedResultsSchema
from api.schemas.query import PaginationSchema
from exceptions.service.pagination import PaginationServiceNotConfiguredError


class PaginationService:
    def __init__(self, request: Request):
        self.is_configured = False
        self._request = request
        self._page: int | None = None
        self._page_size: int | None = None
        self._offset: int | None = None

    def configure(self, pagination: PaginationSchema) -> None:
        """
        Configure the service with pagination information.

        :param pagination: pagination information
        :return:
        """
        self._page = pagination.page
        self._page_size = pagination.page_size
        self._offset = pagination.offset
        self.is_configured = True

    def check_configuration(self, raise_error: bool = False) -> bool:
        """
        Check if the service is configured properly.

        :param raise_error: whether to raise an exception if not configured
        :return: whether the service is configured properly
        """
        if raise_error and not self.is_configured:
            raise PaginationServiceNotConfiguredError()
        return self.is_configured

    def paginate(
        self,
        total: int,
        items: list[BaseSchema],
        result_schema: type[PaginatedResultsSchema],
    ):
        """
        Create a page with a resource list.

        :param total: total number of resource instances
        :param items: list of Pydantic models
        :param result_schema: pagination Pydantic model
        :return: instance of pagination Pydnatic model
        """
        self.check_configuration(raise_error=True)
        return result_schema(
            page=self._page,
            page_size=self._page_size,
            page_count=self._calculate_page_count(total),
            total=total,
            items=items,
            next=self._get_next_page_url(total),
            previous=self._get_previous_page_url(),
        )

    def _get_next_page_url(self, total: int) -> str | None:
        next_page_number = self._calculate_next_page_number(total)
        if next_page_number is not None:
            return self._format_page_number(next_page_number)

    def _get_previous_page_url(self) -> str | None:
        previous_page_number = self._calculate_previous_page_number()
        if previous_page_number is not None:
            return self._format_page_number(previous_page_number)

    def _get_base_url(self) -> str:
        return str(self._request.url).split("?")[0]

    def _format_page_number(self, page_number: int) -> str:
        self._request.url.include_query_params()
        base_url = self._get_base_url()
        return f"{base_url}?page={page_number}&page_size={self._page_size}"

    def _calculate_page_count(self, total: int) -> int:
        return (total + self._page_size - 1) // self._page_size

    def _calculate_next_page_number(self, total: int) -> int | None:
        if self._page * self._page_size < total:
            return self._page + 1

    def _calculate_previous_page_number(self) -> int | None:
        if self._page > 1:
            return self._page - 1
