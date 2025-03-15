"""
Base models for the UP API
"""

from typing import Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, ConfigDict, Field

def to_camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

class UpBaseModel(BaseModel):
    """Base model for all UP API models"""
    model_config = ConfigDict(
        alias_generator=to_camel_case,
        populate_by_name=True,
        alias_to_fields=True
    )

class Links(UpBaseModel):
    """Links object for API resources"""
    self: Optional[str] = None
    related: Optional[str] = None
    prev: Optional[str] = None
    next: Optional[str] = None

class RelationshipData(UpBaseModel):
    """Data object for relationships"""
    type: str
    id: str

class Relationship(UpBaseModel):
    """Relationship object for API resources"""
    data: Optional[Union[RelationshipData, List[RelationshipData]]] = None
    links: Optional[Links] = None

class MoneyObject(UpBaseModel):
    """Money object for currency amounts"""
    currency_code: str
    value: str
    value_in_base_units: int

T = TypeVar("T", bound=BaseModel)

class PaginatedResponse(UpBaseModel, Generic[T]):
    """Base class for paginated responses"""
    data: List[T]
    links: Links 