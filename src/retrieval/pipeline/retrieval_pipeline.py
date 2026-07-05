"""
Production retrieval pipeline.

Complete enterprise retrieval orchestration.
"""

import time
from typing import Dict, Any
from src.conversation.state.domain.conversation_state import ConversationState
from src.conversation.intent.domain.intent_result import IntentResult
from src.knowledge_base.semantic_search import SemanticSearchService
from src.retrieval.domain.entities import SearchQuery
from src.retrieval.pipeline.query.query_builder import ProductionQueryBuilder
from src.retrieval.pipeline.filters.metadata_filter_builder import MetadataFilterBuilder
from src.retrieval.pipeline.ranking.hybrid_ranker import HybridRanker
from src.retrieval.pipeline.compression.duplicate_remover import DuplicateRemover
from src.retrieval.pipeline.compression.context_compressor import ContextCompressor
from src.retrieval.pipeline.validation.retrieval_validator import RetrievalValidator
from src.retrieval.pipeline.pipeline_result import (
    PipelineResult,
    PipelineStatistics,
)
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class RetrievalPipeline:
    """
    Production retrieval pipeline.
    
    Complete enterprise pipeline:
    1. Query Building
    2. Semantic Retrieval
    3. Metadata Filtering
    4. Hybrid Ranking
    5. Duplicate Removal
    6. Context Compression
    7. Validation
    
    Responsibilities:
    - Orchestrate complete retrieval flow
    - Track performance metrics
    - Generate rich diagnostics
    - Return production-ready results
    
    Design:
    - Modular pipeline stages
    - Performance tracking
    - Rich error handling
    - Future extensibility
    """
    
    def __init__(
        self,
        semantic_search: SemanticSearchService,
        query_builder: ProductionQueryBuilder,
        filter_builder: MetadataFilterBuilder,
        ranker: HybridRanker,
        duplicate_remover: DuplicateRemover,
        compressor: ContextCompressor,
        validator: RetrievalValidator,
        top_k: int = 20,
    ) -> None:
        """
        Initialize pipeline.
        
        Args:
            semantic_search: Semantic search service
            query_builder: Query builder
            filter_builder: Metadata filter builder
            ranker: Hybrid ranker
            duplicate_remover: Duplicate remover
            compressor: Context compressor
            validator: Retrieval validator
            top_k: Number of results to retrieve
        """
        self._semantic_search = semantic_search
        self._query_builder = query_builder
        self._filter_builder = filter_builder
        self._ranker = ranker
        self._duplicate_remover = duplicate_remover
        self._compressor = compressor
        self._validator = validator
        self._top_k = top_k
        
        logger.info("RetrievalPipeline initialized")
    
    async def execute(
        self,
        state: ConversationState,
        intent: IntentResult,
    ) -> PipelineResult:
        """
        Execute complete retrieval pipeline.
        
        Args:
            state: Conversation state
            intent: Intent result
        
        Returns:
            Complete pipeline result
        """
        logger.info("Executing retrieval pipeline")
        start_time = time.time()
        
        # Stage 1: Build queries
        query_start = time.time()
        queries = self._query_builder.build_queries(state, intent)
        query_build_ms = (time.time() - query_start) * 1000
        
        # Stage 2: Build filters
        filter_start = time.time()
        filters = self._filter_builder.build_filters(state)
        filtering_ms = (time.time() - filter_start) * 1000
        
        # Stage 3: Semantic retrieval
        retrieval_start = time.time()
        all_results = []
        
        for query_text in queries:
            query = SearchQuery(
                text=query_text,
                filters=filters,
                top_k=self._top_k,
                similarity_threshold=0.0,
            )
            
            results = await self._semantic_search.search(query)
            all_results.extend(results)
            logger.info(f"Query '{query_text[:50]}...' returned {len(results)} results")
        
        retrieval_ms = (time.time() - retrieval_start) * 1000
        chunks_retrieved = len(all_results)
        logger.info(f"STAGE 3: Retrieved {chunks_retrieved} total chunks")
        
        # Stage 4: Hybrid ranking
        ranking_start = time.time()
        ranked_docs = self._ranker.rank(all_results, state)
        ranking_ms = (time.time() - ranking_start) * 1000
        chunks_filtered = len(ranked_docs)
        logger.info(f"STAGE 4: Ranked {chunks_filtered} documents")
        
        # Stage 5: Duplicate removal
        dedup_start = time.time()
        deduplicated = self._duplicate_remover.remove_duplicates(ranked_docs)
        deduplication_ms = (time.time() - dedup_start) * 1000
        chunks_deduplicated = len(deduplicated)
        logger.info(f"STAGE 5: Deduplicated to {chunks_deduplicated} documents")
        
        # Stage 6: Context compression
        compression_start = time.time()
        compressed_context = self._compressor.compress(deduplicated)
        token_count = self._compressor.estimate_tokens(compressed_context)
        compression_ms = (time.time() - compression_start) * 1000
        logger.info(f"STAGE 6: Compressed context, {token_count} tokens")
        
        # Stage 7: Validation
        is_valid, warnings = self._validator.validate(deduplicated)
        logger.info(f"STAGE 7: Validation {'passed' if is_valid else 'failed'}, {len(warnings)} warnings")
        
        # Calculate statistics
        total_latency_ms = (time.time() - start_time) * 1000
        
        statistics = PipelineStatistics(
            total_latency_ms=total_latency_ms,
            query_build_ms=query_build_ms,
            retrieval_ms=retrieval_ms,
            filtering_ms=filtering_ms,
            ranking_ms=ranking_ms,
            deduplication_ms=deduplication_ms,
            compression_ms=compression_ms,
            chunks_retrieved=chunks_retrieved,
            chunks_filtered=chunks_filtered,
            chunks_deduplicated=chunks_deduplicated,
            chunks_final=len(deduplicated),
            assessments_final=len(deduplicated),
            avg_similarity_score=self._calc_avg_similarity(deduplicated),
            avg_ranking_score=self._calc_avg_ranking(deduplicated),
            compression_ratio=self._calc_compression_ratio(
                chunks_retrieved, len(deduplicated)
            ),
            metadata_coverage=self._calc_metadata_coverage(deduplicated),
        )
        
        # Build final result
        result = PipelineResult(
            ranked_documents=deduplicated,
            generated_queries=queries,
            applied_filters=filters,
            retrieval_strategy="semantic_hybrid",
            ranking_strategy="weighted_hybrid",
            decision_rationale=self._build_rationale(state, intent, statistics),
            compressed_context=compressed_context,
            context_token_count=token_count,
            statistics=statistics,
            is_valid=is_valid,
            validation_warnings=warnings,
        )
        
        logger.info(
            f"Pipeline complete: {len(deduplicated)} assessments, "
            f"{total_latency_ms:.1f}ms, valid={is_valid}"
        )
        
        return result
    
    def _calc_avg_similarity(self, docs) -> float:
        """Calculate average similarity score."""
        if not docs:
            return 0.0
        return sum(doc.result.similarity_score for doc in docs) / len(docs)
    
    def _calc_avg_ranking(self, docs) -> float:
        """Calculate average ranking score."""
        if not docs:
            return 0.0
        return sum(doc.ranking_score for doc in docs) / len(docs)
    
    def _calc_compression_ratio(self, original: int, final: int) -> float:
        """Calculate compression ratio."""
        if original == 0:
            return 0.0
        return 1.0 - (final / original)
    
    def _calc_metadata_coverage(self, docs) -> float:
        """Calculate metadata coverage percentage."""
        if not docs:
            return 0.0
        
        complete_count = sum(
            1 for doc in docs
            if doc.result.category and doc.result.test_type
        )
        
        return complete_count / len(docs)
    
    def _build_rationale(
        self,
        state: ConversationState,
        intent: IntentResult,
        stats: PipelineStatistics,
    ) -> str:
        """Build decision rationale."""
        parts = []
        
        parts.append(f"Retrieved {stats.chunks_retrieved} chunks")
        parts.append(f"Ranked and deduplicated to {stats.assessments_final} assessments")
        parts.append(f"Average similarity: {stats.avg_similarity_score:.2f}")
        parts.append(f"Compression ratio: {stats.compression_ratio:.1%}")
        
        return ". ".join(parts)
