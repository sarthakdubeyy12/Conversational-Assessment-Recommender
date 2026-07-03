"""Base shared interfaces."""

from abc import ABC, abstractmethod
from typing import Any


class IRepository(ABC):
    """Base repository interface."""
    
    @abstractmethod
    async def save(self, entity: Any) -> None:
        pass
    
    @abstractmethod
    async def load(self) -> Any:
        pass


class IService(ABC):
    """Base service interface."""
    
    pass
