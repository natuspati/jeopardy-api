from exceptions.module.base import BaseModuleError


class InvalidCLIArgumentsError(BaseModuleError):
    def __init__(self, *arguments: str):
        detail = f"Invalid CLI argument: {arguments}"
        super().__init__(detail)
