"""
Refusal detector.

Detects off-topic requests that should be refused.
"""

from typing import Tuple, List


class RefusalDetector:
    """
    Detects off-topic requests.
    
    Responsibilities:
    - Detect requests outside project scope
    - Identify non-assessment topics
    - Filter out inappropriate requests
    
    Design:
    - Keyword-based detection
    - Topic categorization
    - Conservative refusal (avoid false positives)
    
    Examples of off-topic:
    - Salary questions
    - Resume writing
    - General career advice
    - Unrelated products
    - Personal questions
    """
    
    def __init__(self) -> None:
        """Initialize with off-topic keywords."""
        self._off_topic_keywords = {
            # Career/HR but not assessments
            "salary": 0.8,
            "compensation": 0.7,
            "benefits": 0.7,
            "resume": 0.9,
            "cv": 0.9,
            "interview questions": 0.8,
            "cover letter": 0.9,
            
            # Products/shopping
            "laptop": 0.9,
            "computer": 0.8,
            "phone": 0.9,
            "buy": 0.6,
            "purchase": 0.6,
            "price": 0.5,  # Could be assessment price
            
            # General knowledge
            "world cup": 0.9,
            "weather": 0.9,
            "news": 0.8,
            "recipe": 0.9,
            "movie": 0.9,
            
            # Other services
            "write my": 0.8,
            "do my homework": 0.9,
            "solve this": 0.7,
        }
    
    def detect(self, text: str) -> Tuple[bool, List[str], float]:
        """
        Detect off-topic request.
        
        Args:
            text: User message
        
        Returns:
            (is_off_topic, matched_keywords, confidence)
        """
        text_lower = text.lower()
        matched = []
        max_score = 0.0
        
        for keyword, score in self._off_topic_keywords.items():
            if keyword in text_lower:
                matched.append(keyword)
                max_score = max(max_score, score)
        
        # Only refuse if confidence is high
        is_off_topic = max_score >= 0.7
        
        return is_off_topic, matched, max_score
