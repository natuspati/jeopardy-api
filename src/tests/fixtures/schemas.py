from datetime import datetime

import pytest

from api.schemas.base import BaseSchema
from api.schemas.pagination import PaginatedResultsSchema
from api.schemas.query import DateTimeSchema, OrderSchema, PaginationSchema


class MockSchema(BaseSchema):
    id: int
    name: str


class MockPaginatedResultSchema(PaginatedResultsSchema):
    items: list[MockSchema]


@pytest.fixture(scope="session")
def pagination_schema(default_page: int, default_page_size: int) -> PaginationSchema:
    return PaginationSchema(page=default_page, page_size=default_page_size)


@pytest.fixture(scope="session")
def date_schema(default_timestamp: datetime) -> DateTimeSchema:
    return DateTimeSchema(start=default_timestamp, end=None)


@pytest.fixture(scope="session")
def order_schema() -> OrderSchema:
    return OrderSchema(order="desc")
