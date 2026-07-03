"""
Document builder.

Transforms assessments into searchable documents.
"""

from typing import List
import hashlib

from src.catalog.domain.entities import Assessment
from src.knowledge_base.domain.document import Document
from src.knowledge_base.domain.interfaces import IDocumentBuilder
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class DocumentBuilder(IDocumentBuilder):
    """
    Builds searchable documents from assessments.
    
    Strategy:
    - Creates ONE document per assessment
    - Preserves ALL metadata
    - Generates rich content for embedding
    - Maintains traceability
    
    Document content includes:
    - Assessment name
    - Description
    - Skills and competencies
    - Category and test type
    - Target audience context
    """
    
    def build_documents(self, assessments: List[Assessment]) -> List[Document]:
        """Build documents from assessments."""
        documents = []
        
        for assessment in assessments:
            try:
                document = self._build_document(assessment)
                documents.append(document)
            except Exception as e:
                logger.warning(
                    f"Failed to build document for {assessment.id}: {e}"
                )
        
        logger.info(f"Built {len(documents)} documents from {len(assessments)} assessments")
        return documents
    
    def _build_document(self, assessment: Assessment) -> Document:
        """Build single document from assessment."""
        
        # Generate document ID
        document_id = self._generate_document_id(assessment.id)
        
        # Build rich content for embedding
        content = self._build_content(assessment)
        
        return Document(
            document_id=document_id,
            assessment_id=assessment.id,
            content=content,
            content_type="full",
            assessment_name=assessment.name,
            url=assessment.url,
            description=assessment.description,
            category=assessment.category,
            test_type=assessment.test_type,
            skills_measured=assessment.skills_measured,
            competencies=assessment.competencies,
            duration_minutes=assessment.duration_minutes,
            languages=assessment.languages,
            job_levels=assessment.job_levels,
            industries=assessment.industries,
            tags=assessment.tags,
            metadata={
                "product_code": assessment.product_code,
                "assessment_family": assessment.assessment_family,
                "remote_testing": assessment.remote_testing,
                "adaptive_testing": assessment.adaptive_testing,
                "mobile_compatible": assessment.mobile_compatible,
                "question_count": assessment.question_count,
                "difficulty_level": assessment.difficulty_level,
                "delivery_method": assessment.delivery_method,
            },
        )
    
    def _build_content(self, assessment: Assessment) -> str:
        """
        Build rich content for embedding.
        
        Creates natural language representation suitable for semantic search.
        """
        parts = []
        
        # Name
        parts.append(f"Assessment: {assessment.name}")
        
        # Description
        if assessment.description:
            parts.append(f"Description: {assessment.description}")
        
        # Category and type
        if assessment.category:
            parts.append(f"Category: {assessment.category}")
        if assessment.test_type:
            parts.append(f"Test Type: {assessment.test_type}")
        
        # Skills and competencies
        if assessment.skills_measured:
            skills = ", ".join(assessment.skills_measured)
            parts.append(f"Skills Measured: {skills}")
        
        if assessment.competencies:
            comps = ", ".join(assessment.competencies)
            parts.append(f"Competencies: {comps}")
        
        # Target audience
        if assessment.job_levels:
            levels = ", ".join(assessment.job_levels)
            parts.append(f"Suitable for: {levels}")
        
        if assessment.suitable_roles:
            roles = ", ".join(assessment.suitable_roles)
            parts.append(f"Recommended for roles: {roles}")
        
        if assessment.industries:
            industries = ", ".join(assessment.industries)
            parts.append(f"Industries: {industries}")
        
        # Additional context
        if assessment.duration_minutes:
            parts.append(f"Duration: {assessment.duration_minutes} minutes")
        
        if assessment.languages:
            langs = ", ".join(assessment.languages)
            parts.append(f"Available in: {langs}")
        
        # Tags for additional context
        if assessment.tags:
            tags = ", ".join(assessment.tags)
            parts.append(f"Tags: {tags}")
        
        return " | ".join(parts)
    
    def _generate_document_id(self, assessment_id: str) -> str:
        """Generate unique document ID."""
        content = f"{assessment_id}_full"
        return hashlib.md5(content.encode()).hexdigest()[:16]
