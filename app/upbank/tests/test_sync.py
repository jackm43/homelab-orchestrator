"""
Tests for UP Bank data sync
"""

import os
import unittest
from datetime import datetime
from unittest.mock import Mock, patch
from upbank.sync import UpBankSync
from upbank.models.account import Account, AccountList
from upbank.models.transaction import Transaction, TransactionList
from upbank.models.category import Category, CategoryList
from upbank.models.webhook import Webhook, WebhookList, WebhookLog, WebhookLogList
from upbank.models.base import Links, PaginatedResponse

class TestUpBankSync(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_db_path = "test_sync.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        # Create mock client
        self.mock_client = Mock()
        
        # Create sync instance with mock client
        with patch('upbank.sync.UpClient') as mock_client_class:
            mock_client_class.return_value = self.mock_client
            self.sync = UpBankSync("test-api-key", self.test_db_path)

    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_sync_accounts(self):
        """Test syncing accounts"""
        # Create mock account data
        mock_accounts = AccountList(
            data=[
                Account(
                    type="accounts",
                    id="test-account-1",
                    attributes={
                        "displayName": "Test Account",
                        "accountType": "TRANSACTIONAL",
                        "ownershipType": "INDIVIDUAL",
                        "balance": {
                            "currencyCode": "AUD",
                            "value": "100.00",
                            "valueInBaseUnits": 10000
                        },
                        "createdAt": "2024-01-01T00:00:00+10:00"
                    },
                    relationships={
                        "transactions": {
                            "links": {"related": "test-url"}
                        }
                    },
                    links={"self": "test-url"}
                )
            ],
            links=Links(prev=None, next=None)
        )
        
        # Set up mock response
        self.mock_client.list_accounts.return_value = mock_accounts
        
        # Run sync
        self.sync.sync_accounts()
        
        # Verify account was inserted
        cursor = self.sync.db.conn.execute(
            "SELECT * FROM accounts WHERE id = ?", 
            ("test-account-1",)
        )
        account = cursor.fetchone()
        self.assertIsNotNone(account)
        self.assertEqual(account["display_name"], "Test Account")
        self.assertEqual(account["balance_value"], "100.00")

    def test_sync_transactions(self):
        """Test syncing transactions"""
        # Create mock transaction data
        mock_transactions = TransactionList(
            data=[
                Transaction(
                    type="transactions",
                    id="test-transaction-1",
                    attributes={
                        "status": "SETTLED",
                        "rawText": None,
                        "description": "Test Transaction",
                        "message": None,
                        "isCategorizable": True,
                        "amount": {
                            "currencyCode": "AUD",
                            "value": "-10.00",
                            "valueInBaseUnits": -1000
                        },
                        "createdAt": "2024-01-01T12:00:00+10:00",
                        "settledAt": "2024-01-01T12:00:00+10:00"
                    },
                    relationships={
                        "account": {
                            "data": {
                                "type": "accounts",
                                "id": "test-account-1"
                            }
                        },
                        "tags": {
                            "data": [
                                {
                                    "type": "tags",
                                    "id": "test-tag"
                                }
                            ]
                        }
                    },
                    links={"self": "test-url"}
                )
            ],
            links=Links(prev=None, next=None)
        )
        
        # First insert a test account
        self.sync.db.insert_account({
            "type": "accounts",
            "id": "test-account-1",
            "attributes": {
                "display_name": "Test Account",
                "account_type": "TRANSACTIONAL",
                "ownership_type": "INDIVIDUAL",
                "balance": {
                    "currency_code": "AUD",
                    "value": "100.00",
                    "value_in_base_units": 10000
                },
                "created_at": "2024-01-01T00:00:00+10:00"
            }
        })
        
        # Set up mock response
        self.mock_client.list_transactions.return_value = mock_transactions
        
        # Run sync
        self.sync.sync_transactions()
        
        # Verify transaction was inserted
        cursor = self.sync.db.conn.execute(
            "SELECT * FROM transactions WHERE id = ?", 
            ("test-transaction-1",)
        )
        transaction = cursor.fetchone()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction["description"], "Test Transaction")
        self.assertEqual(transaction["amount_value"], "-10.00")
        
        # Verify tag was inserted and linked
        cursor = self.sync.db.conn.execute("""
            SELECT t.id FROM tags t
            JOIN transaction_tags tt ON t.id = tt.tag_id
            WHERE tt.transaction_id = ?
        """, ("test-transaction-1",))
        tag = cursor.fetchone()
        self.assertIsNotNone(tag)
        self.assertEqual(tag["id"], "test-tag")

    def test_sync_categories(self):
        """Test syncing categories"""
        # Create mock category data
        mock_categories = CategoryList(
            data=[
                Category(
                    type="categories",
                    id="test-category-1",
                    attributes={
                        "name": "Test Category"
                    },
                    relationships={
                        "parent": {
                            "data": None
                        }
                    },
                    links={"self": "test-url"}
                )
            ],
            links=Links(prev=None, next=None)
        )
        
        # Set up mock response
        self.mock_client.list_categories.return_value = mock_categories
        
        # Run sync
        self.sync.sync_categories()
        
        # Verify category was inserted
        cursor = self.sync.db.conn.execute(
            "SELECT * FROM categories WHERE id = ?", 
            ("test-category-1",)
        )
        category = cursor.fetchone()
        self.assertIsNotNone(category)
        self.assertEqual(category["name"], "Test Category")
        self.assertIsNone(category["parent_id"])

    def test_sync_webhooks(self):
        """Test syncing webhooks"""
        # Create mock webhook data
        mock_webhooks = WebhookList(
            data=[
                Webhook(
                    type="webhooks",
                    id="test-webhook-1",
                    attributes={
                        "url": "https://test.com/webhook",
                        "description": "Test Webhook",
                        "secretKey": "test-secret",
                        "createdAt": "2024-01-01T00:00:00+10:00"
                    },
                    relationships={
                        "logs": {
                            "links": {"related": "test-url"}
                        }
                    },
                    links={"self": "test-url"}
                )
            ],
            links=Links(prev=None, next=None)
        )
        
        # Create mock webhook log data
        mock_logs = WebhookLogList(
            data=[
                WebhookLog(
                    id="test-log-1",
                    type="webhook-logs",
                    attributes={
                        "request": {
                            "body": '{"test": "data"}'
                        },
                        "response": {
                            "statusCode": 200,
                            "body": '{"status": "ok"}'
                        },
                        "deliveryStatus": "DELIVERED",
                        "createdAt": "2024-01-01T12:00:00+10:00"
                    },
                    relationships={
                        "webhookEvent": {
                            "data": None,
                            "links": None
                        }
                    },
                    links={"self": "test-url"}
                )
            ],
            links=Links(prev=None, next=None)
        )
        
        # Set up mock responses
        self.mock_client.list_webhooks.return_value = mock_webhooks
        self.mock_client.list_webhook_logs.return_value = mock_logs
        
        # Run sync
        self.sync.sync_webhooks()
        
        # Verify webhook was inserted
        cursor = self.sync.db.conn.execute(
            "SELECT * FROM webhooks WHERE id = ?", 
            ("test-webhook-1",)
        )
        webhook = cursor.fetchone()
        self.assertIsNotNone(webhook)
        self.assertEqual(webhook["url"], "https://test.com/webhook")
        self.assertEqual(webhook["description"], "Test Webhook")
        
        # Verify webhook log was inserted
        cursor = self.sync.db.conn.execute(
            "SELECT * FROM webhook_logs WHERE id = ?", 
            ("test-log-1",)
        )
        log = cursor.fetchone()
        self.assertIsNotNone(log)
        self.assertEqual(log["webhook_id"], "test-webhook-1")
        self.assertEqual(log["response_status_code"], 200)

if __name__ == '__main__':
    unittest.main() 