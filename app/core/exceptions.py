class AppError(Exception):
    """Base exception for application."""

    pass


class NotFoundError(AppError):
    pass


class ValidationError(AppError):
    pass
