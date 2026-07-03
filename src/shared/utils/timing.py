"""Performance timing utilities."""

import time
from contextlib import contextmanager
from typing import Generator


@contextmanager
def timer(operation_name: str) -> Generator:
    """Context manager for timing operations."""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        print(f"{operation_name} took {duration:.2f} seconds")
