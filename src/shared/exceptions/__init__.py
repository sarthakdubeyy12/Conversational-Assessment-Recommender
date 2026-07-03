"""Exceptions module."""

from src.shared.exceptions.base import BaseAppException
from src.shared.exceptions.common_exceptions import (
    ValidationException,
    NotFoundException,
    ConfigurationException,
    InfrastructureException,
    ExternalServiceException,
    TimeoutException,
    UnauthorizedException,
    ForbiddenException,
)

__all__ = [
    "BaseAppException",
    "ValidationException",
    "NotFoundException",
    "ConfigurationException",
    "InfrastructureException",
    "ExternalServiceException",
    "TimeoutException",
    "UnauthorizedException",
    "ForbiddenException",
]
