from datetime import datetime
from typing import Annotated, Literal

from fastapi import Query
from pydantic import ValidationError

from api.schemas.query import DateTimeSchema, OrderSchema, PaginationSchema
from exceptions.http.request import (
    DateTimeQueryParamsApiError,
    OrderQueryParamsApiError,
)
from exceptions.module.schema import SchemaInputError
from settings import settings

PAGE_SIZE_ANNOTATION = Annotated[int, Query(ge=1, le=settings.max_query_limit)]


async def get_pagination_parameters(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: PAGE_SIZE_ANNOTATION = settings.page_size,
) -> PaginationSchema:
    """
    Get pagination from query parameters.

    :param page: page number
    :param page_size: page size
    :return: pagination data with calculated offset
    """
    return PaginationSchema(
        page=page,
        page_size=page_size,
    )


async def get_date_parameters(
    start: Annotated[datetime | None, Query()] = None,
    end: Annotated[datetime | None, Query()] = None,
) -> DateTimeSchema:
    """
    Get start and date from query parameters.

    :param start: start date
    :param end: end date
    :return: start and end dates
    """
    try:
        return DateTimeSchema(
            start=start,
            end=end,
        )
    except ValidationError:
        raise DateTimeQueryParamsApiError()


async def get_order_parameter(
    order: Annotated[Literal["desc", "asc"] | None, Query()] = None,
) -> OrderSchema:
    """
    Get sort order from query parameters.

    :param order: descending or ascending order
    :return: order by parameter
    """
    try:
        return OrderSchema(order=order)
    except SchemaInputError:
        raise OrderQueryParamsApiError()
