"""
Path utilities.

Provides file and directory path operations.
"""

from pathlib import Path
from typing import Optional


def ensure_directory(path: str) -> Path:
    """
    Ensure directory exists, create if not.
    
    Args:
        path: Directory path
    
    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_project_root() -> Path:
    """
    Get project root directory.
    
    Returns:
        Project root Path
    """
    # Assumes this file is in src/shared/utils/
    return Path(__file__).parent.parent.parent.parent


def get_data_directory() -> Path:
    """
    Get data directory path.
    
    Returns:
        Data directory Path
    """
    return get_project_root() / "data"


def get_logs_directory() -> Path:
    """
    Get logs directory path.
    
    Returns:
        Logs directory Path
    """
    logs_dir = get_project_root() / "logs"
    ensure_directory(str(logs_dir))
    return logs_dir


def resolve_path(path: str, base_path: Optional[str] = None) -> Path:
    """
    Resolve path relative to base path.
    
    Args:
        path: Path to resolve
        base_path: Base path (defaults to project root)
    
    Returns:
        Resolved Path
    """
    if base_path is None:
        base_path = str(get_project_root())
    
    path_obj = Path(path)
    if path_obj.is_absolute():
        return path_obj
    
    return (Path(base_path) / path).resolve()


def is_file_exists(path: str) -> bool:
    """
    Check if file exists.
    
    Args:
        path: File path
    
    Returns:
        True if exists, False otherwise
    """
    return Path(path).is_file()


def is_directory_exists(path: str) -> bool:
    """
    Check if directory exists.
    
    Args:
        path: Directory path
    
    Returns:
        True if exists, False otherwise
    """
    return Path(path).is_dir()
