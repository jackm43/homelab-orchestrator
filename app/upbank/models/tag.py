"""
Models for UP Bank tag resources
"""

from typing import Dict, List, Optional
from pydantic import BaseModel

from upbank.models.base import Links, PaginatedResponse, Relationship

class TagRelationships(BaseModel):
    """Relationships for a tag"""
    transactions: Relationship

class Tag(BaseModel):
    """Tag resource"""
    type: str
    id: str
    relationships: TagRelationships

class TagList(PaginatedResponse[Tag]):
    """List of tags response"""
    pass 