class AppError(Exception):
    """Base exception for application."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class NotFoundError(AppError):
    pass


class ValidationError(AppError):
    pass


class ForbiddenError(AppError):
    pass
