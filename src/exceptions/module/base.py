class BaseModuleError(Exception):
    detail: str = "An error occurred"

    def __init__(self, detail=None):
        super().__init__(detail or self.detail)
