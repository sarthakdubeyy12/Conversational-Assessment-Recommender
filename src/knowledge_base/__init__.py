"""
Knowledge Base module.

Responsible for transforming catalog into semantic knowledge base.
"""

from src.knowledge_base.document_builder import DocumentBuilder
from src.knowledge_base.semantic_chunker import SemanticChunker
from src.knowledge_base.index_builder import KnowledgeBaseIndexBuilder
from src.knowledge_base.semantic_search import SemanticSearchService

__all__ = [
    "DocumentBuilder",
    "SemanticChunker",
    "KnowledgeBaseIndexBuilder",
    "SemanticSearchService",
]
