"""
Collection utilities.

Provides utilities for working with lists, dicts, and other collections.
"""

from typing import Any, Dict, List, Optional, TypeVar, Callable


T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    """
    Split list into chunks of specified size.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
    
    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def flatten_list(nested_list: List[List[T]]) -> List[T]:
    """
    Flatten nested list.
    
    Args:
        nested_list: Nested list
    
    Returns:
        Flattened list
    """
    return [item for sublist in nested_list for item in sublist]


def deduplicate_list(items: List[T], key: Optional[Callable[[T], Any]] = None) -> List[T]:
    """
    Remove duplicates from list while preserving order.
    
    Args:
        items: List with potential duplicates
        key: Optional key function for comparison
    
    Returns:
        List without duplicates
    """
    if key is None:
        seen = set()
        result = []
        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
    else:
        seen = set()
        result = []
        for item in items:
            k = key(item)
            if k not in seen:
                seen.add(k)
                result.append(item)
        return result


def safe_get(dictionary: Dict[K, V], key: K, default: Optional[V] = None) -> Optional[V]:
    """
    Safely get value from dictionary.
    
    Args:
        dictionary: Dictionary to get from
        key: Key to look up
        default: Default value if key not found
    
    Returns:
        Value or default
    """
    return dictionary.get(key, default)


def merge_dicts(*dicts: Dict[K, V]) -> Dict[K, V]:
    """
    Merge multiple dictionaries.
    
    Later dictionaries override earlier ones.
    
    Args:
        *dicts: Dictionaries to merge
    
    Returns:
        Merged dictionary
    """
    result: Dict[K, V] = {}
    for d in dicts:
        result.update(d)
    return result


def filter_dict(
    dictionary: Dict[K, V],
    predicate: Callable[[K, V], bool]
) -> Dict[K, V]:
    """
    Filter dictionary by predicate.
    
    Args:
        dictionary: Dictionary to filter
        predicate: Function that returns True to keep item
    
    Returns:
        Filtered dictionary
    """
    return {k: v for k, v in dictionary.items() if predicate(k, v)}


def remove_none_values(dictionary: Dict[K, Optional[V]]) -> Dict[K, V]:
    """
    Remove None values from dictionary.
    
    Args:
        dictionary: Dictionary with potential None values
    
    Returns:
        Dictionary without None values
    """
    return {k: v for k, v in dictionary.items() if v is not None}
