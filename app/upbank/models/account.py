"""
Models for UP Bank account resources
"""

from typing import Dict, List, Optional
from pydantic import Field

from upbank.models.base import Links, PaginatedResponse, Relationship, MoneyObject, UpBaseModel

class AccountAttributes(UpBaseModel):
    """Attributes of an account"""
    display_name: str
    account_type: str
    ownership_type: str
    balance: MoneyObject
    created_at: str

class AccountRelationships(UpBaseModel):
    """Relationships for an account"""
    transactions: Relationship

class Account(UpBaseModel):
    """Account resource"""
    type: str = "accounts"
    id: str
    attributes: AccountAttributes
    relationships: AccountRelationships
    links: Links

class AccountList(PaginatedResponse[Account]):
    """List of accounts response"""
    pass 