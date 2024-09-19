from api.schemas.base import BaseSchema


class PaginatedResultsSchema(BaseSchema):
    page: int
    page_size: int
    page_count: int
    total: int
    items: list[BaseSchema]
    next: str | None
    previous: str | None
