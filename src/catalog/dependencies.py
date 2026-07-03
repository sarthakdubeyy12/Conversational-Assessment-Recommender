"""Catalog dependency injection."""

from src.catalog.application.catalog_service import CatalogService
from src.catalog.infrastructure.json_repository import JSONCatalogRepository
from src.shared.config.settings import Settings


def get_catalog_service() -> CatalogService:
    """Factory for catalog service."""
    settings = Settings()
    repository = JSONCatalogRepository(file_path=settings.catalog_path)
    return CatalogService(repository=repository)
