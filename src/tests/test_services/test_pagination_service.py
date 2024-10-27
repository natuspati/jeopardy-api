from factories.test import TestSchemaFactory
from fixtures.schemas import MockPaginatedResultSchema

from api.schemas.query import PaginationSchema
from api.services.pagination import PaginationService


async def test_paginate(
    batch_size: int,
    pagination_schema: PaginationSchema,
    pagination_service: PaginationService,
):
    page = pagination_schema.page + 1
    pagination_schema.page = page
    page_size = pagination_schema.page_size
    test_schemas = TestSchemaFactory.batch(batch_size)
    selected_schemas = test_schemas[page : page + page_size]  # noqa: E203

    pagination_service.configure(pagination_schema)
    paginated_result = pagination_service.paginate(
        total=batch_size,
        items=selected_schemas,
        result_schema=MockPaginatedResultSchema,
    )
    assert paginated_result.page == page
    assert paginated_result.page_size == page_size
    assert paginated_result.page_count == (batch_size + page_size - 1) // page_size
    assert paginated_result.total == batch_size
    assert len(paginated_result.items) == page_size
    assert f"page={page + 1}" in paginated_result.next
    assert f"page={page - 1}" in paginated_result.previous
    assert f"page_size={page_size}" in paginated_result.next
    assert f"page_size={page_size}" in paginated_result.previous
