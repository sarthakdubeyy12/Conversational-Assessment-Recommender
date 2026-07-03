"""Guardrails domain entities."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ValidationResult:
    """Validation result entity."""
    
    is_valid: bool
    error_message: Optional[str] = None
    violations: List[str] = None


@dataclass(frozen=True)
class SecurityCheck:
    """Security check result."""
    
    passed: bool
    check_type: str
    details: Optional[str] = None
