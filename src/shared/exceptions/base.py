"""Base exception."""


class BaseAppException(Exception):
    """Base exception for application."""
    
    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
