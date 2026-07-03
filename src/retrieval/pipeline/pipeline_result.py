"""
Pipeline result entity.

Complete structured output from retrieval pipeline.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime

from src.retrieval.domain.entities import RetrievalResult


@dataclass(frozen=True)
class RankedDocument:
    """
    Document with ranking score.
    
    Combines retrieval result with hybrid ranking.
    """
    
    result: RetrievalResult
    ranking_score: float
    ranking_factors: Dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class PipelineStatistics:
    """
    Pipeline execution statistics.
    
    Tracks performance and quality metrics.
    """
    
    # Performance
    total_latency_ms: float
    query_build_ms: float
    retrieval_ms: float
    filtering_ms: float
    ranking_ms: float
    deduplication_ms: float
    compression_ms: float
    
    # Retrieval metrics
    chunks_retrieved: int
    chunks_filtered: int
    chunks_deduplicated: int
    chunks_final: int
    assessments_final: int
    
    # Quality metrics
    avg_similarity_score: float
    avg_ranking_score: float
    compression_ratio: float
    metadata_coverage: float


@dataclass(frozen=True)
class PipelineResult:
    """
    Complete retrieval pipeline output.
    
    Single source of truth for recommendation and comparison engines.
    
    Design:
    - Immutable
    - Strongly typed
    - Rich diagnostics
    - Production ready
    """
    
    # Results
    ranked_documents: List[RankedDocument]
    
    # Query context
    generated_queries: List[str]
    applied_filters: Dict[str, Any]
    
    # Retrieval explanation
    retrieval_strategy: str
    ranking_strategy: str
    decision_rationale: str
    
    # Compressed context (token-optimized)
    compressed_context: str
    context_token_count: int
    
    # Statistics
    statistics: PipelineStatistics
    
    # Validation
    is_valid: bool
    validation_warnings: List[str] = field(default_factory=list)
    
    # Metadata
    pipeline_version: str = "1.0"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "ranked_documents": [
                {
                    "result": doc.result.to_dict(),
                    "ranking_score": doc.ranking_score,
                    "ranking_factors": doc.ranking_factors,
                }
                for doc in self.ranked_documents
            ],
            "generated_queries": self.generated_queries,
            "applied_filters": self.applied_filters,
            "retrieval_strategy": self.retrieval_strategy,
            "ranking_strategy": self.ranking_strategy,
            "decision_rationale": self.decision_rationale,
            "compressed_context": self.compressed_context,
            "context_token_count": self.context_token_count,
            "statistics": {
                "total_latency_ms": self.statistics.total_latency_ms,
                "query_build_ms": self.statistics.query_build_ms,
                "retrieval_ms": self.statistics.retrieval_ms,
                "filtering_ms": self.statistics.filtering_ms,
                "ranking_ms": self.statistics.ranking_ms,
                "deduplication_ms": self.statistics.deduplication_ms,
                "compression_ms": self.statistics.compression_ms,
                "chunks_retrieved": self.statistics.chunks_retrieved,
                "chunks_filtered": self.statistics.chunks_filtered,
                "chunks_deduplicated": self.statistics.chunks_deduplicated,
                "chunks_final": self.statistics.chunks_final,
                "assessments_final": self.statistics.assessments_final,
                "avg_similarity_score": self.statistics.avg_similarity_score,
                "avg_ranking_score": self.statistics.avg_ranking_score,
                "compression_ratio": self.statistics.compression_ratio,
                "metadata_coverage": self.statistics.metadata_coverage,
            },
            "is_valid": self.is_valid,
            "validation_warnings": self.validation_warnings,
            "pipeline_version": self.pipeline_version,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def get_top_assessments(self, n: int = 5) -> List[RankedDocument]:
        """Get top N assessments by ranking score."""
        return self.ranked_documents[:n]
    
    def has_results(self) -> bool:
        """Check if pipeline returned results."""
        return len(self.ranked_documents) > 0
