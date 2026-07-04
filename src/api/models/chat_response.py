"""
Chat response model.

Exact schema for outgoing chat responses.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class RecommendationModel(BaseModel):
    """Single assessment recommendation."""
    
    title: str = Field(description="Assessment title")
    url: str = Field(description="Assessment URL")
    
    # Optional fields (may be present depending on engine output)
    description: Optional[str] = Field(
        default=None,
        description="Assessment description"
    )
    competencies: Optional[List[str]] = Field(
        default=None,
        description="Assessed competencies"
    )
    duration: Optional[str] = Field(
        default=None,
        description="Test duration"
    )


class ChatResponse(BaseModel):
    """
    Chat endpoint response model.
    
    Exact schema per assignment requirements:
    {
        "reply": "...",
        "recommendations": [...],
        "end_of_conversation": false
    }
    """
    
    reply: str = Field(
        min_length=1,
        description="Agent response text"
    )
    recommendations: List[RecommendationModel] = Field(
        default_factory=list,
        description="List of assessment recommendations (max 10)"
    )
    end_of_conversation: bool = Field(
        default=False,
        description="Whether conversation has ended"
    )
    
    @field_validator("recommendations")
    @classmethod
    def validate_recommendations(cls, v: List[RecommendationModel]) -> List[RecommendationModel]:
        """Validate recommendations list."""
        if len(v) > 10:
            raise ValueError("Maximum 10 recommendations allowed")
        return v
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "reply": "Based on your needs, I recommend these assessments...",
                "recommendations": [
                    {
                        "title": "Verify G+",
                        "url": "https://www.shl.com/solutions/products/assessments/verify-gplus/",
                        "description": "Measures general cognitive ability",
                        "competencies": ["Problem Solving", "Analytical Thinking"],
                        "duration": "45 minutes"
                    }
                ],
                "end_of_conversation": False
            }
        }
