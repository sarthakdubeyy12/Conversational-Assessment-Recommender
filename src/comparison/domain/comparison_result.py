"""
Comparison result entities.

Strongly-typed output from comparison engine.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime
from enum import Enum


class FieldStatus(str, Enum):
    """Field comparison status."""
    IDENTICAL = "identical"
    DIFFERENT = "different"
    MISSING_IN_A = "missing_in_a"
    MISSING_IN_B = "missing_in_b"
    MISSING_IN_BOTH = "missing_in_both"


class ConfidenceLevel(str, Enum):
    """Comparison confidence level."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class AssessmentInfo:
    """
    Assessment information for comparison.
    
    Complete catalog data for one assessment.
    """
    
    assessment_id: str
    assessment_name: str
    official_url: str
    category: str = ""
    test_type: str = ""
    description: str = ""
    skills: List[str] = field(default_factory=list)
    competencies: List[str] = field(default_factory=list)
    duration_minutes: int = 0
    languages: List[str] = field(default_factory=list)
    job_levels: List[str] = field(default_factory=list)
    industries: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Traceability
    retrieval_rank: int = 0
    chunk_id: str = ""
    similarity_score: float = 0.0


@dataclass(frozen=True)
class FieldComparison:
    """Single field comparison result."""
    
    field_name: str
    status: FieldStatus
    value_a: Any = None
    value_b: Any = None


@dataclass(frozen=True)
class ComparisonStatistics:
    """
    Comparison processing statistics.
    """
    
    processing_time_ms: float
    retrieval_time_ms: float
    comparison_time_ms: float
    fields_compared: int
    fields_identical: int
    fields_different: int
    fields_missing: int
    similarities_found: int
    differences_found: int


@dataclass(frozen=True)
class ComparisonResult:
    """
    Complete comparison engine output.
    
    Catalog-grounded comparison of assessments.
    
    Design:
    - Immutable
    - Strongly typed
    - Fully traceable
    - No hallucination
    """
    
    # Assessments being compared (required)
    assessment_a: AssessmentInfo
    assessment_b: AssessmentInfo
    
    # Comparison results (required)
    similarities: List[str]
    differences: List[str]
    field_comparisons: List[FieldComparison]
    
    # Unique strengths (required)
    unique_strengths_a: List[str]
    unique_strengths_b: List[str]
    
    # Missing information (required)
    missing_fields_a: List[str]
    missing_fields_b: List[str]
    
    # Confidence (required)
    confidence: ConfidenceLevel
    confidence_score: float
    
    # Statistics (required)
    statistics: ComparisonStatistics
    
    # Grounding evidence (required)
    retrieval_source: str
    
    # Optional fields with defaults
    missing_information_note: str = ""
    catalog_references: List[str] = field(default_factory=list)
    structured_context: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "assessment_a": {
                "id": self.assessment_a.assessment_id,
                "name": self.assessment_a.assessment_name,
                "url": self.assessment_a.official_url,
                "category": self.assessment_a.category,
                "test_type": self.assessment_a.test_type,
                "description": self.assessment_a.description[:200],
                "skills": self.assessment_a.skills,
                "competencies": self.assessment_a.competencies,
                "duration_minutes": self.assessment_a.duration_minutes,
            },
            "assessment_b": {
                "id": self.assessment_b.assessment_id,
                "name": self.assessment_b.assessment_name,
                "url": self.assessment_b.official_url,
                "category": self.assessment_b.category,
                "test_type": self.assessment_b.test_type,
                "description": self.assessment_b.description[:200],
                "skills": self.assessment_b.skills,
                "competencies": self.assessment_b.competencies,
                "duration_minutes": self.assessment_b.duration_minutes,
            },
            "similarities": self.similarities,
            "differences": self.differences,
            "unique_strengths_a": self.unique_strengths_a,
            "unique_strengths_b": self.unique_strengths_b,
            "missing_fields_a": self.missing_fields_a,
            "missing_fields_b": self.missing_fields_b,
            "confidence": self.confidence.value,
            "confidence_score": self.confidence_score,
            "statistics": {
                "processing_time_ms": self.statistics.processing_time_ms,
                "fields_compared": self.statistics.fields_compared,
                "fields_identical": self.statistics.fields_identical,
                "fields_different": self.statistics.fields_different,
                "similarities_found": self.statistics.similarities_found,
                "differences_found": self.statistics.differences_found,
            },
            "timestamp": self.timestamp.isoformat(),
        }
