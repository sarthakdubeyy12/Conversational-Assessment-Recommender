"""
Knowledge base index builder.

Orchestrates the complete indexing pipeline.
"""

from typing import List
from src.catalog.domain.entities import Assessment
from src.knowledge_base.domain.interfaces import (
    IDocumentBuilder,
    ISemanticChunker,
    IEmbeddingProvider,
    IVectorStore,
)
from src.knowledge_base.embeddings.batch_processor import EmbeddingBatchProcessor
from src.knowledge_base.embeddings.embedding_cache import EmbeddingCache
from src.shared.logging.logger import get_logger
from src.shared.utils.timing import Stopwatch

logger = get_logger(__name__)


class KnowledgeBaseIndexBuilder:
    """
    Builds knowledge base index from catalog.
    
    Pipeline:
    1. Load assessments from catalog
    2. Build documents
    3. Chunk documents
    4. Generate embeddings (with caching)
    5. Store in vector database
    
    Responsibilities:
    - Orchestrate indexing pipeline
    - Handle incremental updates
    - Report progress
    - Validate index
    
    Design:
    - Supports both full rebuild and incremental updates
    - Uses embedding cache to avoid recomputation
    - Batch processing for efficiency
    - Comprehensive logging
    """
    
    def __init__(
        self,
        document_builder: IDocumentBuilder,
        chunker: ISemanticChunker,
        embedding_provider: IEmbeddingProvider,
        vector_store: IVectorStore,
        enable_cache: bool = True,
    ) -> None:
        """
        Initialize index builder.
        
        Args:
            document_builder: Document builder
            chunker: Semantic chunker
            embedding_provider: Embedding provider
            vector_store: Vector store
            enable_cache: Enable embedding cache
        """
        self._document_builder = document_builder
        self._chunker = chunker
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        
        # Initialize batch processor
        self._batch_processor = EmbeddingBatchProcessor(embedding_provider)
        
        # Initialize cache
        self._cache = None
        if enable_cache:
            self._cache = EmbeddingCache()
        
        logger.info("KnowledgeBaseIndexBuilder initialized")
    
    async def build_index(
        self,
        assessments: List[Assessment],
        collection_name: str,
        rebuild: bool = False,
    ) -> dict:
        """
        Build complete knowledge base index.
        
        Args:
            assessments: Assessments to index
            collection_name: Collection name
            rebuild: Whether to rebuild (delete existing)
        
        Returns:
            Build statistics
        """
        logger.info("=" * 60)
        logger.info("KNOWLEDGE BASE INDEXING STARTED")
        logger.info("=" * 60)
        
        timer = Stopwatch()
        timer.start()
        
        stats = {
            "assessments": len(assessments),
            "documents": 0,
            "chunks": 0,
            "embeddings_generated": 0,
            "embeddings_cached": 0,
            "vectors_stored": 0,
        }
        
        try:
            # Step 1: Create/load collection
            logger.info("Step 1/5: Initializing vector store...")
            dimension = self._embedding_provider.get_dimension()
            
            if rebuild:
                await self._vector_store.delete_all()
                logger.info("Existing collection deleted")
            
            await self._vector_store.create_collection(collection_name, dimension)
            
            # Step 2: Build documents
            logger.info("Step 2/5: Building documents...")
            documents = self._document_builder.build_documents(assessments)
            stats["documents"] = len(documents)
            logger.info(f"Built {len(documents)} documents")
            
            if not documents:
                logger.warning("No documents built. Exiting.")
                return stats
            
            # Step 3: Chunk documents
            logger.info("Step 3/5: Chunking documents...")
            chunks = self._chunker.chunk_documents(documents)
            stats["chunks"] = len(chunks)
            logger.info(f"Created {len(chunks)} chunks")
            
            if not chunks:
                logger.warning("No chunks created. Exiting.")
                return stats
            
            # Step 4: Generate embeddings
            logger.info("Step 4/5: Generating embeddings...")
            texts = [chunk.text for chunk in chunks]
            
            embeddings, cache_stats = self._generate_embeddings_with_cache(texts)
            stats["embeddings_generated"] = cache_stats["generated"]
            stats["embeddings_cached"] = cache_stats["cached"]
            
            logger.info(
                f"Embeddings: {cache_stats['generated']} generated, "
                f"{cache_stats['cached']} from cache"
            )
            
            # Step 5: Store in vector database
            logger.info("Step 5/5: Storing vectors...")
            await self._vector_store.add_chunks(chunks, embeddings)
            stats["vectors_stored"] = len(chunks)
            logger.info(f"Stored {len(chunks)} vectors")
            
            # Save cache
            if self._cache:
                self._cache.save()
            
            elapsed = timer.elapsed()
            
            logger.info("=" * 60)
            logger.info("KNOWLEDGE BASE INDEXING COMPLETED")
            logger.info(f"Total time: {elapsed:.2f}s")
            logger.info(f"Assessments: {stats['assessments']}")
            logger.info(f"Documents: {stats['documents']}")
            logger.info(f"Chunks: {stats['chunks']}")
            logger.info(f"Embeddings generated: {stats['embeddings_generated']}")
            logger.info(f"Embeddings cached: {stats['embeddings_cached']}")
            logger.info(f"Vectors stored: {stats['vectors_stored']}")
            logger.info("=" * 60)
            
            return stats
            
        except Exception as e:
            logger.error(f"Index building failed: {e}", exc_info=True)
            raise
    
    def _generate_embeddings_with_cache(
        self,
        texts: List[str],
    ) -> tuple:
        """
        Generate embeddings with caching.
        
        Returns:
            (embeddings, stats)
        """
        if not self._cache:
            # No cache, generate all
            embeddings = self._batch_processor.process_batch(texts)
            return embeddings, {"generated": len(texts), "cached": 0}
        
        # Check cache
        cached = self._cache.get_batch(texts)
        
        # Find texts needing embedding
        texts_to_embed = [t for t in texts if t not in cached]
        
        # Generate missing embeddings
        new_embeddings = []
        if texts_to_embed:
            new_embeddings = self._batch_processor.process_batch(
                texts_to_embed,
                show_progress=True,
            )
            
            # Cache new embeddings
            pairs = list(zip(texts_to_embed, new_embeddings))
            self._cache.set_batch(pairs)
        
        # Combine cached and new embeddings in original order
        embeddings = []
        new_idx = 0
        for text in texts:
            if text in cached:
                embeddings.append(cached[text])
            else:
                embeddings.append(new_embeddings[new_idx])
                new_idx += 1
        
        return embeddings, {
            "generated": len(texts_to_embed),
            "cached": len(cached),
        }
