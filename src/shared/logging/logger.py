"""Logger setup."""

import logging
import sys
from typing import Optional


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Setup application logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(name)
