from typing import Self

from pydantic import model_validator

from api.schemas.base import BaseSchema
from exceptions.service.schema import SchemaInputError


class PaginatedResultsSchema(BaseSchema):
    page: int
    page_size: int
    page_count: int
    total: int
    items: list[BaseSchema]
    next: str | None
    previous: str | None

    @model_validator(mode="after")
    def check_number_of_items(self) -> Self:
        """
        Check that number of items does not exceed page size.

        :return:
        """
        if len(self.items) > self.page_size:
            raise SchemaInputError("Number of items cannot be higher than page size.")
        return self
