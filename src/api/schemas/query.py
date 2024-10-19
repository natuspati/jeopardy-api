from datetime import datetime
from typing import Literal, Self

from pydantic import field_validator, model_validator
from pydantic_core.core_schema import ValidationInfo

from api.enums import OrderQueryEnum
from api.schemas.base import BaseSchema
from exceptions.service.request import DateTimeQueryParamsError, OrderQueryParamsError


class PaginationSchema(BaseSchema):
    page: int
    page_size: int
    offset: int = 0

    @model_validator(mode="before")
    @classmethod
    def calculate_offset(
        cls,
        page_info: dict[str, str | int],
        validation_info: ValidationInfo,
    ) -> dict[str, int]:
        """
        Calculate the offset for pagination.

        :param page_info: input value for pagination
        :param validation_info: validation information
        :return: pagination dictionary with calculated offset
        """
        if not page_info.get("offset"):
            page = int(page_info["page"])
            page_size = int(page_info["page_size"])
            page_info["offset"] = (page - 1) * page_size
        return page_info


class DateTimeSchema(BaseSchema):
    start: datetime | None = None
    end: datetime | None = None

    @model_validator(mode="after")
    def check_start_before_end(self) -> Self:
        """
        Check that the start date is before end date.

        :return:
        """
        if self.start and self.end:
            if self.start >= self.end:
                raise DateTimeQueryParamsError()
        return self


class OrderSchema(BaseSchema):
    order: OrderQueryEnum

    @field_validator("order", mode="before")
    @classmethod
    def validate_order(
        cls,
        order_value: Literal["desc", "asc"] | None,
    ) -> OrderQueryEnum:
        """
        Convert input order to order enum.

        :param order_value: order as a string or None
        :return: order enum
        """
        if order_value is None:
            return OrderQueryEnum.desc

        try:
            return OrderQueryEnum(order_value)
        except ValueError:
            raise OrderQueryParamsError()
