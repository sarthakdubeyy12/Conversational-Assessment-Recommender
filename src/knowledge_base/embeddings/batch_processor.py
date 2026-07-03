"""
Batch embedding processor.

Handles efficient batch processing of embeddings.
"""

from typing import List, Tuple
from src.knowledge_base.domain.interfaces import IEmbeddingProvider
from src.shared.logging.logger import get_logger
from src.shared.utils.timing import Stopwatch

logger = get_logger(__name__)


class EmbeddingBatchProcessor:
    """
    Processes embeddings in batches.
    
    Responsibilities:
    - Batch text efficiently
    - Handle retries on failure
    - Report progress
    - Optimize memory usage
    
    Design:
    - Processes in configurable batch sizes
    - Tracks progress
    - Handles partial failures gracefully
    """
    
    def __init__(
        self,
        provider: IEmbeddingProvider,
        batch_size: int = 32,
        max_retries: int = 3,
    ) -> None:
        """
        Initialize batch processor.
        
        Args:
            provider: Embedding provider
            batch_size: Batch size for processing
            max_retries: Maximum retries on failure
        """
        self._provider = provider
        self._batch_size = batch_size
        self._max_retries = max_retries
    
    def process_batch(
        self,
        texts: List[str],
        show_progress: bool = True,
    ) -> List[List[float]]:
        """
        Process texts in batches.
        
        Args:
            texts: List of texts to embed
            show_progress: Whether to log progress
        
        Returns:
            List of embeddings
        """
        if not texts:
            return []
        
        timer = Stopwatch()
        timer.start()
        
        total = len(texts)
        embeddings = []
        
        # Process in batches
        for i in range(0, total, self._batch_size):
            batch = texts[i:i + self._batch_size]
            batch_num = (i // self._batch_size) + 1
            total_batches = (total + self._batch_size - 1) // self._batch_size
            
            if show_progress and batch_num % 10 == 0:
                logger.info(
                    f"Processing batch {batch_num}/{total_batches} "
                    f"({i}/{total} texts)"
                )
            
            # Process with retries
            batch_embeddings = self._process_with_retry(batch)
            embeddings.extend(batch_embeddings)
        
        elapsed = timer.elapsed()
        rate = total / elapsed if elapsed > 0 else 0
        
        logger.info(
            f"Processed {total} embeddings in {elapsed:.2f}s "
            f"({rate:.0f} texts/sec)"
        )
        
        return embeddings
    
    def _process_with_retry(self, batch: List[str]) -> List[List[float]]:
        """Process batch with retry logic."""
        for attempt in range(self._max_retries):
            try:
                return self._provider.embed_batch(batch)
            except Exception as e:
                if attempt == self._max_retries - 1:
                    logger.error(
                        f"Failed to process batch after {self._max_retries} "
                        f"attempts: {e}"
                    )
                    raise
                logger.warning(
                    f"Batch processing failed (attempt {attempt + 1}/"
                    f"{self._max_retries}): {e}"
                )
