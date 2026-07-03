"""
Common type aliases and definitions.

Provides consistent type hints across the application.
"""

from typing import Any, Dict, List, Union

# JSON types
JSON = Union[Dict[str, Any], List[Any], str, int, float, bool, None]
JSONDict = Dict[str, Any]
JSONList = List[Any]

# HTTP types
Headers = Dict[str, str]
QueryParams = Dict[str, Union[str, int, float, bool]]

# Common aliases
ID = str
Timestamp = str
