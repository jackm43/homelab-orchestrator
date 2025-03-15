"""
Models for UP Bank transaction resources
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import Field

from upbank.models.base import Links, PaginatedResponse, Relationship, RelationshipData, MoneyObject, UpBaseModel

class HoldInfo(UpBaseModel):
    """Hold info object"""
    amount: MoneyObject
    foreign_amount: Optional[MoneyObject] = None

class CardPurchaseMethod(UpBaseModel):
    """Card purchase method object"""
    method: str
    device_id: Optional[str] = None

class Note(UpBaseModel):
    """Note object"""
    value: str
    created_at: datetime

class Customer(UpBaseModel):
    """Customer object"""
    id: Optional[str] = None
    display_name: str = Field(alias="displayName")

class TransactionAttributes(UpBaseModel):
    """Attributes of a transaction"""
    status: str
    raw_text: Optional[str] = None
    description: str
    message: Optional[str] = None
    is_categorizable: bool
    hold_info: Optional[HoldInfo] = Field(default=None, alias="holdInfo")
    round_up: Optional[MoneyObject] = Field(default=None, alias="roundUp")
    cashback: Optional[MoneyObject] = None
    amount: MoneyObject
    foreign_amount: Optional[MoneyObject] = Field(default=None, alias="foreignAmount")
    card_purchase_method: Optional[CardPurchaseMethod] = Field(default=None, alias="cardPurchaseMethod")
    settled_at: Optional[datetime] = Field(default=None, alias="settledAt")
    created_at: datetime = Field(alias="createdAt")
    transaction_type: Optional[str] = Field(default=None, alias="transactionType")
    note: Optional[Note] = None
    performing_customer: Optional[Customer] = Field(default=None, alias="performingCustomer")

class TransactionRelationships(UpBaseModel):
    """Relationships for a transaction"""
    account: Relationship = Field(default_factory=lambda: Relationship(data=RelationshipData(type="accounts", id="")))
    transfer_account: Optional[Relationship] = Field(default_factory=lambda: Relationship(data=None))
    category: Optional[Relationship] = Field(default_factory=lambda: Relationship(data=None))
    parent_category: Optional[Relationship] = Field(default_factory=lambda: Relationship(data=None))
    tags: Relationship = Field(default_factory=lambda: Relationship(data=[]))

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "account": {
                        "data": {
                            "type": "accounts",
                            "id": "test-account-id"
                        },
                        "links": {
                            "related": "https://api.up.com.au/api/v1/accounts/test-account-id"
                        }
                    },
                    "transfer_account": {
                        "data": None,
                        "links": {
                            "related": None
                        }
                    },
                    "category": {
                        "data": None,
                        "links": {
                            "related": None
                        }
                    },
                    "parent_category": {
                        "data": None,
                        "links": {
                            "related": None
                        }
                    },
                    "tags": {
                        "data": [],
                        "links": {
                            "related": "https://api.up.com.au/api/v1/transactions/test-transaction-id/tags"
                        }
                    }
                }
            ]
        }
    }

class Transaction(UpBaseModel):
    """Transaction resource"""
    type: str = "transactions"
    id: str
    attributes: TransactionAttributes
    relationships: TransactionRelationships
    links: Links

    model_config = {
        "populate_by_name": True
    }

class TransactionList(PaginatedResponse[Transaction]):
    """List of transactions response"""
    pass