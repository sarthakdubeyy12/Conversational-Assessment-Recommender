"""
Recall Calculator.

Computes Recall@K metrics for recommendation evaluation.

Recall@K = (# expected assessments in top K) / (# expected assessments)

Responsibilities:
- Compute Recall@1, @3, @5, @10
- Handle missing/empty recommendations
- Handle missing/empty expected assessments
- Generate ranking quality metrics
"""

from typing import List, Dict, Any


class RecallCalculator:
    """
    Recall@K calculator for recommendation evaluation.
    
    Used to measure how many expected assessments appear
    in the top K recommended assessments.
    """
    
    @staticmethod
    def calculate_recall_at_k(
        recommendations: List[Dict[str, Any]],
        expected_assessments: List[str],
        k: int,
    ) -> float:
        """
        Calculate Recall@K.
        
        Args:
            recommendations: List of recommended assessments
            expected_assessments: List of expected assessment URLs
            k: Top K to consider
        
        Returns:
            Recall@K score [0.0, 1.0]
        """
        if not expected_assessments:
            return 1.0  # No expectations = perfect recall
        
        if not recommendations:
            return 0.0  # No recommendations = zero recall
        
        # Extract URLs from top K recommendations
        recommended_urls = [
            rec.get("url", "") for rec in recommendations[:k]
        ]
        
        # Count matches
        matches = sum(
            1 for expected in expected_assessments
            if expected in recommended_urls
        )
        
        return matches / len(expected_assessments)
    
    @staticmethod
    def calculate_all_recalls(
        recommendations: List[Dict[str, Any]],
        expected_assessments: List[str],
    ) -> Dict[str, float]:
        """
        Calculate Recall@1, @3, @5, @10.
        
        Args:
            recommendations: List of recommended assessments
            expected_assessments: List of expected assessment URLs
        
        Returns:
            Dictionary with recall@1, recall@3, recall@5, recall@10
        """
        return {
            "recall@1": RecallCalculator.calculate_recall_at_k(
                recommendations, expected_assessments, 1
            ),
            "recall@3": RecallCalculator.calculate_recall_at_k(
                recommendations, expected_assessments, 3
            ),
            "recall@5": RecallCalculator.calculate_recall_at_k(
                recommendations, expected_assessments, 5
            ),
            "recall@10": RecallCalculator.calculate_recall_at_k(
                recommendations, expected_assessments, 10
            ),
        }
    
    @staticmethod
    def calculate_mean_recall(
        results: List[Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Calculate mean recall across multiple results.
        
        Args:
            results: List of recall dictionaries
        
        Returns:
            Mean recall for each K
        """
        if not results:
            return {
                "recall@1": 0.0,
                "recall@3": 0.0,
                "recall@5": 0.0,
                "recall@10": 0.0,
            }
        
        return {
            "recall@1": sum(r["recall@1"] for r in results) / len(results),
            "recall@3": sum(r["recall@3"] for r in results) / len(results),
            "recall@5": sum(r["recall@5"] for r in results) / len(results),
            "recall@10": sum(r["recall@10"] for r in results) / len(results),
        }
    
    @staticmethod
    def calculate_precision_at_k(
        recommendations: List[Dict[str, Any]],
        expected_assessments: List[str],
        k: int,
    ) -> float:
        """
        Calculate Precision@K.
        
        Precision@K = (# expected in top K) / K
        
        Args:
            recommendations: List of recommended assessments
            expected_assessments: List of expected assessment URLs
            k: Top K to consider
        
        Returns:
            Precision@K score [0.0, 1.0]
        """
        if not recommendations:
            return 0.0
        
        # Extract URLs from top K recommendations
        recommended_urls = [
            rec.get("url", "") for rec in recommendations[:k]
        ]
        
        # Count matches
        matches = sum(
            1 for url in recommended_urls
            if url in expected_assessments
        )
        
        return matches / min(k, len(recommended_urls))
