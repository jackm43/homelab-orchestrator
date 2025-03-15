"""
Tests for the UP Bank API models
"""

import pytest
from pydantic import ValidationError
import unittest

from upbank.models import (
    Account,
    AccountList,
    Transaction,
    TransactionList,
    Category,
    CategoryList,
    Tag,
    TagList,
    Webhook,
    WebhookList,
)
from upbank.models.base import MoneyObject, Links, Relationship, RelationshipData

def test_money_object():
    """Test MoneyObject model"""
    data = {
        "currencyCode": "AUD",
        "value": "100.00",
        "valueInBaseUnits": 10000
    }
    money = MoneyObject.model_validate(data)
    assert money.currency_code == "AUD"
    assert money.value == "100.00"
    assert money.value_in_base_units == 10000

def test_money_object_validation():
    """Test MoneyObject validation"""
    with pytest.raises(ValidationError):
        MoneyObject.model_validate({
            "currencyCode": "AUD",
            "value": "not a number",
            "valueInBaseUnits": "not an integer"
        })

def test_links():
    """Test Links model"""
    data = {
        "self": "https://api.up.com.au/api/v1/test",
        "related": "https://api.up.com.au/api/v1/test/related",
        "prev": None,
        "next": "https://api.up.com.au/api/v1/test?page=2"
    }
    links = Links.model_validate(data)
    assert links.self == "https://api.up.com.au/api/v1/test"
    assert links.related == "https://api.up.com.au/api/v1/test/related"
    assert links.prev is None
    assert links.next == "https://api.up.com.au/api/v1/test?page=2"

def test_relationship():
    """Test Relationship model"""
    data = {
        "data": {
            "type": "test",
            "id": "test-id"
        },
        "links": {
            "self": "https://api.up.com.au/api/v1/test",
            "related": "https://api.up.com.au/api/v1/test/related"
        }
    }
    relationship = Relationship.model_validate(data)
    assert relationship.data.type == "test"
    assert relationship.data.id == "test-id"
    assert relationship.links.self == "https://api.up.com.au/api/v1/test"

def test_account(account_response):
    """Test Account model"""
    account = Account.model_validate(account_response["data"])
    assert account.type == "accounts"
    assert account.id == "test-account-id"
    assert account.attributes.display_name == "Test Account"
    assert account.attributes.account_type == "SAVER"
    assert account.attributes.balance.value == "100.00"

def test_transaction(transaction_response):
    """Test Transaction model"""
    transaction = Transaction.model_validate(transaction_response["data"])
    assert transaction.type == "transactions"
    assert transaction.id == "test-transaction-id"
    assert transaction.attributes.status == "SETTLED"
    assert transaction.attributes.description == "Test Transaction"
    assert transaction.attributes.amount.value == "-10.00"

def test_category(category_response):
    """Test Category model"""
    category = Category.model_validate(category_response["data"])
    assert category.type == "categories"
    assert category.id == "test-category-id"
    assert category.attributes.name == "Test Category"
    assert category.relationships.parent.data is None

def test_webhook(webhook_response):
    """Test Webhook model"""
    webhook = Webhook.model_validate(webhook_response["data"])
    assert webhook.type == "webhooks"
    assert webhook.id == "test-webhook-id"
    assert webhook.attributes.url == "https://example.com/webhook"
    assert webhook.attributes.description == "Test Webhook"
    assert webhook.attributes.secret_key == "test-secret-key"

def test_paginated_response(account_response):
    """Test PaginatedResponse model"""
    data = {
        "data": [account_response["data"]],
        "links": {
            "prev": None,
            "next": "https://api.up.com.au/api/v1/accounts?page=2"
        }
    }
    accounts = AccountList.model_validate(data)
    assert len(accounts.data) == 1
    assert isinstance(accounts.data[0], Account)
    assert accounts.links.prev is None
    assert accounts.links.next == "https://api.up.com.au/api/v1/accounts?page=2" 