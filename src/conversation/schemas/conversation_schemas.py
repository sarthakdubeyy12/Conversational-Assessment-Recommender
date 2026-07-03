"""Conversation Pydantic schemas."""

from typing import List, Optional
from pydantic import BaseModel


class MessageSchema(BaseModel):
    role: str
    content: str


class ChatRequestSchema(BaseModel):
    messages: List[MessageSchema]


class RecommendationItemSchema(BaseModel):
    name: str
    url: str
    test_type: str


class ChatResponseSchema(BaseModel):
    reply: str
    recommendations: List[RecommendationItemSchema] = []
    end_of_conversation: bool = False
