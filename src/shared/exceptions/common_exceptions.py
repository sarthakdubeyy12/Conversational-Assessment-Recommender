"""
Common reusable exceptions.

Generic exceptions used across multiple features.
"""

from typing import Any, Dict, Optional
from src.shared.exceptions.base import BaseAppException


class ValidationException(BaseAppException):
    """
    Raised when validation fails.
    
    Used for:
    - Input validation errors
    - Schema validation errors
    - Business rule violations
    """
    
    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        error_details = details or {}
        if field:
            error_details["field"] = field
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=error_details
        )


class NotFoundException(BaseAppException):
    """
    Raised when resource is not found.
    
    Used for:
    - Missing database records
    - Missing files
    - Missing configuration
    """
    
    def __init__(
        self,
        resource_type: str,
        resource_id: Optional[str] = None,
        message: Optional[str] = None
    ) -> None:
        if message is None:
            message = f"{resource_type} not found"
            if resource_id:
                message = f"{resource_type} with ID '{resource_id}' not found"
        
        details = {"resource_type": resource_type}
        if resource_id:
            details["resource_id"] = resource_id
        
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details=details
        )


class ConfigurationException(BaseAppException):
    """
    Raised when configuration is invalid or missing.
    
    Used for:
    - Missing environment variables
    - Invalid configuration values
    - Configuration loading errors
    """
    
    def __init__(
        self,
        message: str = "Configuration error",
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        error_details = details or {}
        if config_key:
            error_details["config_key"] = config_key
        
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=500,
            details=error_details
        )


class InfrastructureException(BaseAppException):
    """
    Raised when infrastructure fails.
    
    Used for:
    - Database connection errors
    - File system errors
    - Network errors
    """
    
    def __init__(
        self,
        message: str = "Infrastructure error",
        component: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        error_details = details or {}
        if component:
            error_details["component"] = component
        
        super().__init__(
            message=message,
            error_code="INFRASTRUCTURE_ERROR",
            status_code=500,
            details=error_details
        )


class ExternalServiceException(BaseAppException):
    """
    Raised when external service call fails.
    
    Used for:
    - LLM API errors
    - Third-party API errors
    - Timeout errors
    """
    
    def __init__(
        self,
        service_name: str,
        message: str = "External service error",
        status_code: int = 503,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        error_details = details or {}
        error_details["service_name"] = service_name
        
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=status_code,
            details=error_details
        )


class TimeoutException(BaseAppException):
    """
    Raised when operation times out.
    
    Used for:
    - Request timeouts
    - Operation timeouts
    - Connection timeouts
    """
    
    def __init__(
        self,
        operation: str,
        timeout_seconds: int,
        message: Optional[str] = None
    ) -> None:
        if message is None:
            message = f"Operation '{operation}' timed out after {timeout_seconds}s"
        
        super().__init__(
            message=message,
            error_code="TIMEOUT_ERROR",
            status_code=408,
            details={
                "operation": operation,
                "timeout_seconds": timeout_seconds
            }
        )


class UnauthorizedException(BaseAppException):
    """
    Raised when authentication fails.
    
    Used for:
    - Missing credentials
    - Invalid credentials
    - Expired tokens
    """
    
    def __init__(
        self,
        message: str = "Unauthorized",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=401,
            details=details or {}
        )


class ForbiddenException(BaseAppException):
    """
    Raised when access is forbidden.
    
    Used for:
    - Insufficient permissions
    - Access denied
    - Rate limiting
    """
    
    def __init__(
        self,
        message: str = "Forbidden",
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        error_details = details or {}
        if resource:
            error_details["resource"] = resource
        
        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            status_code=403,
            details=error_details
        )
