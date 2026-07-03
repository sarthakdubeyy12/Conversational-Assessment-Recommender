"""
Semantic chunker.

Splits documents into semantically meaningful chunks.
"""

from typing import List
import hashlib

from src.knowledge_base.domain.document import Document, DocumentChunk
from src.knowledge_base.domain.interfaces import ISemanticChunker
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class SemanticChunker(ISemanticChunker):
    """
    Semantic document chunker.
    
    Strategy:
    - For catalog data, creates focused chunks by semantic section
    - Each chunk preserves full metadata for filtering
    - Maintains assessment context in every chunk
    
    Chunk types:
    - overview: Name + description + category
    - skills: Skills and competencies
    - context: Job levels, roles, industries
    - full: Complete assessment (for small assessments)
    
    Design rationale:
    - Catalog assessments are already concise (< 500 tokens typically)
    - Better to create semantic sections than arbitrary character splits
    - Preserves semantic meaning and searchability
    """
    
    def __init__(
        self,
        max_chunk_length: int = 512,
        create_overview_chunk: bool = True,
        create_skills_chunk: bool = True,
        create_full_chunk: bool = True,
    ) -> None:
        """
        Initialize chunker.
        
        Args:
            max_chunk_length: Maximum chunk length in characters
            create_overview_chunk: Create overview chunks
            create_skills_chunk: Create skills-focused chunks
            create_full_chunk: Create full content chunks
        """
        self._max_chunk_length = max_chunk_length
        self._create_overview = create_overview_chunk
        self._create_skills = create_skills_chunk
        self._create_full = create_full_chunk
    
    def chunk_documents(self, documents: List[Document]) -> List[DocumentChunk]:
        """Chunk multiple documents."""
        all_chunks = []
        
        for document in documents:
            chunks = self.chunk_document(document)
            all_chunks.extend(chunks)
        
        logger.info(
            f"Chunked {len(documents)} documents into {len(all_chunks)} chunks "
            f"(avg {len(all_chunks) / len(documents):.1f} chunks/doc)"
        )
        
        return all_chunks
    
    def chunk_document(self, document: Document) -> List[DocumentChunk]:
        """
        Chunk single document.
        
        Creates multiple semantically focused chunks from one document.
        """
        chunks = []
        chunk_index = 0
        
        # Chunk 1: Overview (name + description + category)
        if self._create_overview:
            overview_chunk = self._create_overview_chunk(document, chunk_index)
            if overview_chunk:
                chunks.append(overview_chunk)
                chunk_index += 1
        
        # Chunk 2: Skills and competencies
        if self._create_skills and (
            document.skills_measured or document.competencies
        ):
            skills_chunk = self._create_skills_chunk(document, chunk_index)
            if skills_chunk:
                chunks.append(skills_chunk)
                chunk_index += 1
        
        # Chunk 3: Full content (for complete context)
        if self._create_full:
            full_chunk = self._create_full_content_chunk(document, chunk_index)
            if full_chunk:
                chunks.append(full_chunk)
                chunk_index += 1
        
        return chunks
    
    def _create_overview_chunk(
        self,
        document: Document,
        index: int,
    ) -> DocumentChunk:
        """Create overview chunk."""
        parts = [document.assessment_name]
        
        if document.description:
            parts.append(document.description)
        
        if document.category:
            parts.append(f"Category: {document.category}")
        
        if document.test_type:
            parts.append(f"Type: {document.test_type}")
        
        text = " | ".join(parts)
        
        return self._create_chunk(
            document=document,
            text=text,
            chunk_type="overview",
            index=index,
        )
    
    def _create_skills_chunk(
        self,
        document: Document,
        index: int,
    ) -> DocumentChunk:
        """Create skills-focused chunk."""
        parts = [f"{document.assessment_name} measures"]
        
        if document.skills_measured:
            skills = ", ".join(document.skills_measured)
            parts.append(f"Skills: {skills}")
        
        if document.competencies:
            comps = ", ".join(document.competencies)
            parts.append(f"Competencies: {comps}")
        
        text = " | ".join(parts)
        
        return self._create_chunk(
            document=document,
            text=text,
            chunk_type="skills",
            index=index,
        )
    
    def _create_full_content_chunk(
        self,
        document: Document,
        index: int,
    ) -> DocumentChunk:
        """Create full content chunk."""
        # Use the pre-built rich content
        text = document.content
        
        # If too long, truncate (shouldn't happen for catalog data)
        if len(text) > self._max_chunk_length:
            text = text[:self._max_chunk_length] + "..."
            logger.debug(
                f"Truncated long content for {document.assessment_id}"
            )
        
        return self._create_chunk(
            document=document,
            text=text,
            chunk_type="full",
            index=index,
        )
    
    def _create_chunk(
        self,
        document: Document,
        text: str,
        chunk_type: str,
        index: int,
    ) -> DocumentChunk:
        """Create document chunk with metadata."""
        chunk_id = self._generate_chunk_id(
            document.document_id,
            chunk_type,
            index,
        )
        
        return DocumentChunk(
            chunk_id=chunk_id,
            document_id=document.document_id,
            assessment_id=document.assessment_id,
            chunk_index=index,
            text=text,
            chunk_type=chunk_type,
            assessment_name=document.assessment_name,
            url=document.url,
            category=document.category,
            test_type=document.test_type,
            skills_measured=document.skills_measured,
            competencies=document.competencies,
            duration_minutes=document.duration_minutes,
            languages=document.languages,
            job_levels=document.job_levels,
            industries=document.industries,
            tags=document.tags,
            metadata=document.metadata,
        )
    
    def _generate_chunk_id(
        self,
        document_id: str,
        chunk_type: str,
        index: int,
    ) -> str:
        """Generate unique chunk ID."""
        content = f"{document_id}_{chunk_type}_{index}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
