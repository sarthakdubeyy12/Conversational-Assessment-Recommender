"""
Knowledge Base exceptions.

Domain-specific exceptions for knowledge base operations.
"""

from src.shared.exceptions.base import BaseApplicationException


class KnowledgeBaseException(BaseApplicationException):
    """Base knowledge base exception."""
    pass


class EmbeddingException(KnowledgeBaseException):
    """Embedding generation failed."""
    pass


class VectorStoreException(KnowledgeBaseException):
    """Vector store operation failed."""
    pass


class IndexBuildException(KnowledgeBaseException):
    """Index building failed."""
    pass


class SearchException(KnowledgeBaseException):
    """Search operation failed."""
    pass
