"""
HTML parser component.

Extracts structured assessment data from HTML pages.
Handles various HTML structures and missing fields gracefully.
"""

from typing import Optional, List
from datetime import datetime
import re
from bs4 import BeautifulSoup

from src.catalog.domain.entities import Assessment, ScrapedPage
from src.catalog.domain.interfaces import IHTMLParser
from src.shared.logging.logger import get_logger
from src.shared.utils.uuid_utils import generate_uuid
from src.shared.utils.hash_utils import hash_string

logger = get_logger(__name__)


class AssessmentHTMLParser(IHTMLParser):
    """
    Parses HTML pages to extract assessment data.
    
    Extracts all available structured metadata from assessment pages.
    Handles missing fields gracefully - only extracts what exists.
    """
    
    def parse(self, page: ScrapedPage) -> Optional[Assessment]:
        """
        Parse HTML page to extract assessment data.
        
        Args:
            page: Scraped page with HTML content
        
        Returns:
            Assessment object or None if parsing fails
        """
        try:
            soup = BeautifulSoup(page.html_content, "html.parser")
            
            # Extract title/name (required)
            name = self._extract_name(soup)
            if not name:
                logger.warning(f"No title found for {page.url}")
                return None
            
            # Generate ID from URL
            assessment_id = hash_string(page.url)[:16]
            
            # Extract all available fields
            assessment = Assessment(
                id=assessment_id,
                name=name,
                url=page.url,
                description=self._extract_description(soup),
                category=self._extract_category(soup),
                test_type=self._extract_test_type(soup),
                skills_measured=self._extract_skills(soup),
                competencies=self._extract_competencies(soup),
                duration_minutes=self._extract_duration(soup),
                question_count=self._extract_question_count(soup),
                languages=self._extract_languages(soup),
                remote_testing=self._extract_remote_testing(soup),
                adaptive_testing=self._extract_adaptive_testing(soup),
                mobile_compatible=self._extract_mobile_compatible(soup),
                job_levels=self._extract_job_levels(soup),
                suitable_roles=self._extract_suitable_roles(soup),
                industries=self._extract_industries(soup),
                product_code=self._extract_product_code(soup),
                assessment_family=self._extract_assessment_family(soup),
                version=self._extract_version(soup),
                tags=self._extract_tags(soup),
                difficulty_level=self._extract_difficulty_level(soup),
                delivery_method=self._extract_delivery_method(soup),
                metadata=self._extract_metadata(soup),
                scraped_at=page.scraped_at,
                last_updated=datetime.utcnow(),
            )
            
            logger.info(f"Successfully parsed: {name}")
            return assessment
            
        except Exception as e:
            logger.error(f"Error parsing {page.url}: {e}", exc_info=True)
            return None
    
    def _extract_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract assessment name/title."""
        # Try multiple selectors
        selectors = [
            ("h1", {}),
            ("title", {}),
            ("h2", {"class": "product-title"}),
            ("div", {"class": "assessment-name"}),
        ]
        
        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)
        
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract assessment description."""
        selectors = [
            ("meta", {"name": "description"}),
            ("div", {"class": "description"}),
            ("p", {"class": "product-description"}),
        ]
        
        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element:
                if tag == "meta":
                    return element.get("content", "").strip()
                else:
                    return element.get_text(strip=True)
        
        return None
    
    def _extract_category(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract assessment category."""
        element = soup.find("span", {"class": "category"})
        if element:
            return element.get_text(strip=True)
        return None
    
    def _extract_test_type(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract test type."""
        element = soup.find("span", {"class": "test-type"})
        if element:
            return element.get_text(strip=True)
        return None
    
    def _extract_skills(self, soup: BeautifulSoup) -> List[str]:
        """Extract skills measured."""
        skills = []
        
        # Try different patterns
        elements = soup.find_all("li", {"class": "skill"})
        for elem in elements:
            skill = elem.get_text(strip=True)
            if skill:
                skills.append(skill)
        
        return skills
    
    def _extract_competencies(self, soup: BeautifulSoup) -> List[str]:
        """Extract competencies."""
        competencies = []
        
        elements = soup.find_all("li", {"class": "competency"})
        for elem in elements:
            comp = elem.get_text(strip=True)
            if comp:
                competencies.append(comp)
        
        return competencies
    
    def _extract_duration(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract duration in minutes."""
        element = soup.find(text=re.compile(r"(\d+)\s*minutes?", re.I))
        if element:
            match = re.search(r"(\d+)\s*minutes?", element, re.I)
            if match:
                return int(match.group(1))
        return None
    
    def _extract_question_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract number of questions."""
        element = soup.find(text=re.compile(r"(\d+)\s*questions?", re.I))
        if element:
            match = re.search(r"(\d+)\s*questions?", element, re.I)
            if match:
                return int(match.group(1))
        return None
    
    def _extract_languages(self, soup: BeautifulSoup) -> List[str]:
        """Extract supported languages."""
        languages = []
        
        elements = soup.find_all("li", {"class": "language"})
        for elem in elements:
            lang = elem.get_text(strip=True)
            if lang:
                languages.append(lang)
        
        return languages
    
    def _extract_remote_testing(self, soup: BeautifulSoup) -> bool:
        """Check if remote testing is supported."""
        text = soup.get_text().lower()
        return "remote testing" in text or "online testing" in text
    
    def _extract_adaptive_testing(self, soup: BeautifulSoup) -> bool:
        """Check if adaptive testing is supported."""
        text = soup.get_text().lower()
        return "adaptive" in text or "computer adaptive" in text
    
    def _extract_mobile_compatible(self, soup: BeautifulSoup) -> bool:
        """Check if mobile compatible."""
        text = soup.get_text().lower()
        return "mobile" in text or "tablet" in text
    
    def _extract_job_levels(self, soup: BeautifulSoup) -> List[str]:
        """Extract target job levels."""
        levels = []
        
        elements = soup.find_all("li", {"class": "job-level"})
        for elem in elements:
            level = elem.get_text(strip=True)
            if level:
                levels.append(level)
        
        return levels
    
    def _extract_suitable_roles(self, soup: BeautifulSoup) -> List[str]:
        """Extract suitable roles."""
        roles = []
        
        elements = soup.find_all("li", {"class": "role"})
        for elem in elements:
            role = elem.get_text(strip=True)
            if role:
                roles.append(role)
        
        return roles
    
    def _extract_industries(self, soup: BeautifulSoup) -> List[str]:
        """Extract industries."""
        industries = []
        
        elements = soup.find_all("li", {"class": "industry"})
        for elem in elements:
            industry = elem.get_text(strip=True)
            if industry:
                industries.append(industry)
        
        return industries
    
    def _extract_product_code(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product code."""
        element = soup.find("span", {"class": "product-code"})
        if element:
            return element.get_text(strip=True)
        return None
    
    def _extract_assessment_family(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract assessment family."""
        element = soup.find("span", {"class": "assessment-family"})
        if element:
            return element.get_text(strip=True)
        return None
    
    def _extract_version(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract version."""
        element = soup.find(text=re.compile(r"version\s+(\d+\.?\d*)", re.I))
        if element:
            match = re.search(r"version\s+(\d+\.?\d*)", element, re.I)
            if match:
                return match.group(1)
        return None
    
    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract tags."""
        tags = []
        
        elements = soup.find_all("span", {"class": "tag"})
        for elem in elements:
            tag = elem.get_text(strip=True)
            if tag:
                tags.append(tag)
        
        return tags
    
    def _extract_difficulty_level(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract difficulty level."""
        element = soup.find("span", {"class": "difficulty"})
        if element:
            return element.get_text(strip=True)
        return None
    
    def _extract_delivery_method(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract delivery method."""
        element = soup.find("span", {"class": "delivery-method"})
        if element:
            return element.get_text(strip=True)
        return None
    
    def _extract_metadata(self, soup: BeautifulSoup) -> dict:
        """Extract additional metadata."""
        metadata = {}
        
        # Extract any meta tags
        meta_tags = soup.find_all("meta")
        for meta in meta_tags:
            name = meta.get("name") or meta.get("property")
            content = meta.get("content")
            if name and content:
                metadata[name] = content
        
        return metadata
