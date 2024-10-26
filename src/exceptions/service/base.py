from fastapi import status


class BaseError(Exception):
    detail: str = "Error occurred"

    def __init__(self, detail: str | None = None):
        super().__init__(detail or self.detail)


class BaseServiceError(BaseError):
    detail: str = "Internal service error"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    ws_status_code = status.WS_1011_INTERNAL_ERROR

    def __init__(
        self,
        detail: str | None = None,
        status_code: int | None = None,
        ws_status_code: int | None = None,
    ):
        super().__init__(detail or self.detail)
        self.status_code = status_code or self.status_code  # noqa: WPS601
        self.ws_status_code = ws_status_code or self.ws_status_code  # noqa: WPS601
