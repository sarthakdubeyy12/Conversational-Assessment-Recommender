"""
Recommendation result entities.

Strongly-typed output from recommendation engine.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime


@dataclass(frozen=True)
class AssessmentRecommendation:
    """
    Single assessment recommendation.
    
    Complete information for a recommended assessment.
    Traceable back to catalog and retrieval pipeline.
    """
    
    # Identification
    assessment_id: str
    assessment_name: str
    official_url: str
    
    # Classification
    test_type: str
    category: str
    
    # Matching information
    matching_skills: List[str] = field(default_factory=list)
    matching_competencies: List[str] = field(default_factory=list)
    
    # Scoring
    ranking_score: float = 0.0
    similarity_score: float = 0.0
    metadata_score: float = 0.0
    skill_score: float = 0.0
    
    # Explanation
    recommendation_reason: str = ""
    matching_factors: List[str] = field(default_factory=list)
    
    # Catalog metadata
    duration_minutes: int = 0
    languages: List[str] = field(default_factory=list)
    job_levels: List[str] = field(default_factory=list)
    industries: List[str] = field(default_factory=list)
    
    # Traceability
    retrieval_rank: int = 0
    chunk_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "assessment_id": self.assessment_id,
            "assessment_name": self.assessment_name,
            "official_url": self.official_url,
            "test_type": self.test_type,
            "category": self.category,
            "matching_skills": self.matching_skills,
            "matching_competencies": self.matching_competencies,
            "ranking_score": self.ranking_score,
            "similarity_score": self.similarity_score,
            "metadata_score": self.metadata_score,
            "skill_score": self.skill_score,
            "recommendation_reason": self.recommendation_reason,
            "matching_factors": self.matching_factors,
            "duration_minutes": self.duration_minutes,
            "languages": self.languages,
            "job_levels": self.job_levels,
            "industries": self.industries,
            "retrieval_rank": self.retrieval_rank,
        }


@dataclass(frozen=True)
class RecommendationStatistics:
    """
    Recommendation engine statistics.
    
    Tracks processing metrics and quality indicators.
    """
    
    # Processing metrics
    candidates_received: int
    candidates_filtered: int
    candidates_validated: int
    recommendations_generated: int
    processing_time_ms: float
    
    # Quality metrics
    avg_ranking_score: float
    avg_similarity_score: float
    score_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Filtering metrics
    invalid_urls: int = 0
    missing_metadata: int = 0
    duplicates_removed: int = 0
    low_confidence: int = 0


@dataclass(frozen=True)
class RecommendationResult:
    """
    Complete recommendation engine output.
    
    Single source of truth for recommended assessments.
    
    Design:
    - Immutable
    - Strongly typed
    - Fully traceable
    - Rich diagnostics
    """
    
    # Recommendations
    recommendations: List[AssessmentRecommendation]
    
    # Metadata
    confidence: str  # "high", "medium", "low"
    total_candidates: int
    retrieval_source: str
    
    # Statistics
    statistics: RecommendationStatistics
    
    # Validation
    is_valid: bool
    validation_warnings: List[str] = field(default_factory=list)
    
    # Reasoning
    decision_rationale: str = ""
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "recommendations": [rec.to_dict() for rec in self.recommendations],
            "confidence": self.confidence,
            "total_candidates": self.total_candidates,
            "retrieval_source": self.retrieval_source,
            "statistics": {
                "candidates_received": self.statistics.candidates_received,
                "candidates_filtered": self.statistics.candidates_filtered,
                "candidates_validated": self.statistics.candidates_validated,
                "recommendations_generated": self.statistics.recommendations_generated,
                "processing_time_ms": self.statistics.processing_time_ms,
                "avg_ranking_score": self.statistics.avg_ranking_score,
                "avg_similarity_score": self.statistics.avg_similarity_score,
                "invalid_urls": self.statistics.invalid_urls,
                "missing_metadata": self.statistics.missing_metadata,
                "duplicates_removed": self.statistics.duplicates_removed,
                "low_confidence": self.statistics.low_confidence,
            },
            "is_valid": self.is_valid,
            "validation_warnings": self.validation_warnings,
            "decision_rationale": self.decision_rationale,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def has_recommendations(self) -> bool:
        """Check if any recommendations exist."""
        return len(self.recommendations) > 0
    
    def get_top_recommendations(self, n: int = 5) -> List[AssessmentRecommendation]:
        """Get top N recommendations."""
        return self.recommendations[:n]
