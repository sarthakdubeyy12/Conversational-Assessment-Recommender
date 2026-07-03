"""Catalog data validators."""


class URLValidator:
    """Validates SHL URLs."""
    
    def is_valid_shl_url(self, url: str) -> bool:
        pass


class AssessmentValidator:
    """Validates assessment data."""
    
    def validate(self, data: dict) -> bool:
        pass
