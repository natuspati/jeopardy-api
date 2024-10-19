from fastapi import status


class BaseError(Exception):
    detail: str = "Error occurred"

    def __init__(self, detail: str | None = None):
        super().__init__(detail or self.detail)


class BaseServiceError(BaseError):
    detail: str = "Internal service error"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        detail: str | None = None,
        status_code: int | None = None,
    ):
        super().__init__(detail or self.detail)
        self.status_code = status_code or self.status_code  # noqa: WPS601