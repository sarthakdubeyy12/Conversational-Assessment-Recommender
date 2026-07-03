"""
Hashing utilities.

Provides consistent hashing functions.
"""

import hashlib
from typing import Union


def hash_string(text: str, algorithm: str = "sha256") -> str:
    """
    Hash a string using specified algorithm.
    
    Args:
        text: Text to hash
        algorithm: Hash algorithm (md5, sha1, sha256, sha512)
    
    Returns:
        Hex digest of hash
    """
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode("utf-8"))
    return hash_obj.hexdigest()


def hash_bytes(data: bytes, algorithm: str = "sha256") -> str:
    """
    Hash bytes using specified algorithm.
    
    Args:
        data: Bytes to hash
        algorithm: Hash algorithm
    
    Returns:
        Hex digest of hash
    """
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(data)
    return hash_obj.hexdigest()


def generate_checksum(content: Union[str, bytes]) -> str:
    """
    Generate MD5 checksum for content.
    
    Args:
        content: Content to checksum
    
    Returns:
        MD5 checksum
    """
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.md5(content).hexdigest()


def generate_content_hash(content: Union[str, bytes]) -> str:
    """
    Generate SHA256 hash for content.
    
    Suitable for content addressable storage.
    
    Args:
        content: Content to hash
    
    Returns:
        SHA256 hash
    """
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()
