"""
Hallucination Detector.

Detects when system invents information not in catalog.

Responsibilities:
- Detect invented assessment URLs
- Detect invented assessment names
- Detect invented metadata
- Detect unsupported claims
"""

from typing import List, Dict, Any, Set
import re


class HallucinationDetector:
    """
    Detects hallucinations in system output.
    
    Hallucination = any information not grounded in the catalog.
    """
    
    def __init__(self, known_assessment_urls: Set[str] = None):
        """
        Initialize detector.
        
        Args:
            known_assessment_urls: Set of valid assessment URLs from catalog
        """
        self._known_urls = known_assessment_urls or set()
    
    def detect_url_hallucinations(
        self,
        recommendations: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Detect invented assessment URLs.
        
        Args:
            recommendations: List of recommendations
        
        Returns:
            List of hallucinated recommendations
        """
        hallucinations = []
        
        for rec in recommendations:
            url = rec.get("url", "")
            
            # Check if URL is in known catalog
            if self._known_urls and url not in self._known_urls:
                hallucinations.append({
                    "type": "invented_url",
                    "url": url,
                    "title": rec.get("title", ""),
                    "recommendation": rec,
                })
            
            # Check for malformed URLs
            if not self._is_valid_shl_url(url):
                hallucinations.append({
                    "type": "malformed_url",
                    "url": url,
                    "title": rec.get("title", ""),
                    "recommendation": rec,
                })
        
        return hallucinations
    
    def detect_text_hallucinations(
        self,
        text: str,
    ) -> List[Dict[str, Any]]:
        """
        Detect hallucinations in text response.
        
        Args:
            text: Text to analyze
        
        Returns:
            List of detected hallucinations
        """
        hallucinations = []
        
        # Detect invented URLs in text
        url_pattern = r'https://www\.shl\.com/[^\s]+'
        found_urls = re.findall(url_pattern, text)
        
        for url in found_urls:
            if self._known_urls and url not in self._known_urls:
                hallucinations.append({
                    "type": "invented_url_in_text",
                    "url": url,
                    "context": text,
                })
        
        # Detect unsupported certainty claims
        certainty_patterns = [
            r'definitely',
            r'certainly',
            r'guaranteed',
            r'always',
            r'never',
            r'100%',
        ]
        
        for pattern in certainty_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                hallucinations.append({
                    "type": "unsupported_certainty",
                    "pattern": pattern,
                    "context": text,
                })
        
        return hallucinations
    
    def _is_valid_shl_url(self, url: str) -> bool:
        """
        Check if URL is a valid SHL assessment URL.
        
        Args:
            url: URL to check
        
        Returns:
            True if valid SHL URL
        """
        if not url:
            return False
        
        # Must be HTTPS SHL domain
        if not url.startswith("https://www.shl.com/"):
            return False
        
        # Must have reasonable length
        if len(url) < 30 or len(url) > 200:
            return False
        
        return True
    
    def get_summary(
        self,
        recommendations: List[Dict[str, Any]],
        text: str = "",
    ) -> Dict[str, Any]:
        """
        Get hallucination summary.
        
        Args:
            recommendations: List of recommendations
            text: Text response
        
        Returns:
            Summary of hallucinations
        """
        url_hallucinations = self.detect_url_hallucinations(recommendations)
        text_hallucinations = self.detect_text_hallucinations(text) if text else []
        
        total_hallucinations = len(url_hallucinations) + len(text_hallucinations)
        
        return {
            "total_hallucinations": total_hallucinations,
            "url_hallucinations": len(url_hallucinations),
            "text_hallucinations": len(text_hallucinations),
            "details": {
                "url_issues": url_hallucinations,
                "text_issues": text_hallucinations,
            },
        }
