"""
Tests for the UP Bank API client
"""

import pytest
from unittest.mock import patch, MagicMock

from upbank.client import UpClient
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

@pytest.fixture
def client():
    """Create a test client"""
    with patch("requests.Session") as mock_session:
        mock = MagicMock()
        mock.request = MagicMock()
        mock.request.return_value = MagicMock()
        mock.request.return_value.status_code = 200
        mock.request.return_value.content = True
        mock.request.return_value.json.return_value = {}
        mock_session.return_value = mock
        client = UpClient("test-token")
        return client

def test_client_initialization():
    """Test client initialization"""
    client = UpClient("test-token")
    assert client.token == "test-token"
    assert client.base_url == "https://api.up.com.au/api/v1"
    assert "Authorization" in client.headers
    assert client.headers["Authorization"] == "Bearer test-token"

def test_get_accounts(client, account_response):
    """Test get_accounts method"""
    response = {
        "data": [account_response["data"]],
        "links": {"self": "test"}
    }
    client.session.request.return_value.json.return_value = response

    accounts = client.get_accounts()
    assert isinstance(accounts, AccountList)
    assert len(accounts.data) == 1
    assert accounts.data[0].id == "test-account-id"

def test_get_account(client, account_response):
    """Test get_account method"""
    client.session.request.return_value.json.return_value = account_response

    account = client.get_account("test-account-id")
    assert isinstance(account, Account)
    assert account.id == "test-account-id"

def test_get_transactions(client, transaction_response):
    """Test get_transactions method"""
    response = {
        "data": [transaction_response["data"]],
        "links": {"self": "test"}
    }
    client.session.request.return_value.json.return_value = response

    transactions = client.get_transactions()
    assert isinstance(transactions, TransactionList)
    assert len(transactions.data) == 1
    assert transactions.data[0].id == "test-transaction-id"

def test_get_transaction(client, transaction_response):
    """Test get_transaction method"""
    client.session.request.return_value.json.return_value = transaction_response

    transaction = client.get_transaction("test-transaction-id")
    assert isinstance(transaction, Transaction)
    assert transaction.id == "test-transaction-id"

def test_get_categories(client, category_response):
    """Test get_categories method"""
    response = {
        "data": [category_response["data"]],
        "links": {"self": "test"}
    }
    client.session.request.return_value.json.return_value = response

    categories = client.get_categories()
    assert isinstance(categories, CategoryList)
    assert len(categories.data) == 1
    assert categories.data[0].id == "test-category-id"

def test_get_category(client, category_response):
    """Test get_category method"""
    client.session.request.return_value.json.return_value = category_response

    category = client.get_category("test-category-id")
    assert isinstance(category, Category)
    assert category.id == "test-category-id"

def test_get_webhooks(client, webhook_response):
    """Test get_webhooks method"""
    response = {
        "data": [webhook_response["data"]],
        "links": {"self": "test"}
    }
    client.session.request.return_value.json.return_value = response

    webhooks = client.get_webhooks()
    assert isinstance(webhooks, WebhookList)
    assert len(webhooks.data) == 1
    assert webhooks.data[0].id == "test-webhook-id"

def test_get_webhook(client, webhook_response):
    """Test get_webhook method"""
    client.session.request.return_value.json.return_value = webhook_response

    webhook = client.get_webhook("test-webhook-id")
    assert isinstance(webhook, Webhook)
    assert webhook.id == "test-webhook-id"

def test_create_webhook(client, webhook_response):
    """Test create_webhook method"""
    client.session.request.return_value.json.return_value = webhook_response

    webhook = client.create_webhook(
        url="https://example.com/webhook",
        description="Test Webhook"
    )
    assert isinstance(webhook, Webhook)
    assert webhook.id == "test-webhook-id"

def test_delete_webhook(client):
    """Test delete_webhook method"""
    client.session.request.return_value.status_code = 204
    client.session.request.return_value.content = False

    client.delete_webhook("test-webhook-id")

def test_ping(client):
    """Test ping method"""
    response = {
        "meta": {
            "id": "test-ping-id",
            "statusEmoji": "✅"
        }
    }
    client.session.request.return_value.json.return_value = response

    result = client.ping()
    assert result["meta"]["id"] == "test-ping-id" 