"""
Models for UP Bank category resources
"""

from typing import Dict, List, Optional
from pydantic import Field

from upbank.models.base import Links, PaginatedResponse, Relationship, UpBaseModel

class CategoryAttributes(UpBaseModel):
    """Attributes of a category"""
    name: str

class CategoryRelationships(UpBaseModel):
    """Relationships for a category"""
    parent: Relationship

class Category(UpBaseModel):
    """Category resource"""
    type: str = "categories"
    id: str
    attributes: CategoryAttributes
    relationships: CategoryRelationships
    links: Links

class CategoryList(PaginatedResponse[Category]):
    """List of categories response"""
    pass 