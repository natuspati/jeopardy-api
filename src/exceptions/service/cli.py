from exceptions.service.base import BaseError


class InvalidCLIArgumentsError(BaseError):
    def __init__(self, *arguments: str):
        detail = f"Invalid CLI argument: {arguments}"
        super().__init__(detail)
