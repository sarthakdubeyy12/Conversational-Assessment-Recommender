"""
Chat request model.

Exact schema for incoming chat requests.
"""

from typing import List, Literal
from pydantic import BaseModel, Field, field_validator


class MessageModel(BaseModel):
    """Single conversation message."""
    
    role: Literal["user", "assistant"] = Field(
        description="Message role (user or assistant)"
    )
    content: str = Field(
        min_length=1,
        description="Message content"
    )
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content is not empty."""
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()


class ChatRequest(BaseModel):
    """
    Chat endpoint request model.
    
    Exact schema per assignment requirements:
    {
        "messages": [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
    }
    """
    
    messages: List[MessageModel] = Field(
        min_length=1,
        description="Conversation messages (at least one required)"
    )
    
    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v: List[MessageModel]) -> List[MessageModel]:
        """Validate messages list."""
        if not v:
            raise ValueError("At least one message is required")
        
        # Last message must be from user
        if v[-1].role != "user":
            raise ValueError("Last message must be from user")
        
        return v
    
    def get_current_message(self) -> str:
        """Get current user message."""
        return self.messages[-1].content
    
    def get_history(self) -> List[MessageModel]:
        """Get conversation history (all except last message)."""
        return self.messages[:-1] if len(self.messages) > 1 else []
