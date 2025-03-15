"""
Tests for the UP Bank database operations
"""

import os
import unittest
from datetime import datetime
from upbank.database import UpDatabase

class TestUpDatabase(unittest.TestCase):
    def setUp(self):
        """Set up test database"""
        self.test_db_path = "test_upbank.db"
        self.db = UpDatabase(self.test_db_path)

    def tearDown(self):
        """Clean up after tests"""
        self.db.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_insert_account(self):
        """Test inserting an account"""
        account_data = {
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
        }

        self.db.insert_account(account_data)

        # Verify the account was inserted
        cursor = self.db.conn.execute("SELECT * FROM accounts WHERE id = ?", ("test-account-1",))
        account = cursor.fetchone()
        self.assertIsNotNone(account)
        self.assertEqual(account["display_name"], "Test Account")
        self.assertEqual(account["balance_value"], "100.00")

    def test_insert_transaction(self):
        """Test inserting a transaction"""
        # First insert a test account
        account_data = {
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
        }
        self.db.insert_account(account_data)

        # Now insert a transaction
        transaction_data = {
            "type": "transactions",
            "id": "test-transaction-1",
            "attributes": {
                "status": "SETTLED",
                "raw_text": None,
                "description": "Test Transaction",
                "message": None,
                "is_categorizable": True,
                "amount": {
                    "currency_code": "AUD",
                    "value": "-10.00",
                    "value_in_base_units": -1000
                },
                "created_at": "2024-01-01T12:00:00+10:00",
                "settled_at": "2024-01-01T12:00:00+10:00"
            },
            "relationships": {
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
            }
        }

        self.db.insert_transaction(transaction_data)

        # Verify the transaction was inserted
        cursor = self.db.conn.execute("SELECT * FROM transactions WHERE id = ?", ("test-transaction-1",))
        transaction = cursor.fetchone()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction["description"], "Test Transaction")
        self.assertEqual(transaction["amount_value"], "-10.00")

        # Verify the tag was inserted and linked
        cursor = self.db.conn.execute("""
            SELECT t.id FROM tags t
            JOIN transaction_tags tt ON t.id = tt.tag_id
            WHERE tt.transaction_id = ?
        """, ("test-transaction-1",))
        tag = cursor.fetchone()
        self.assertIsNotNone(tag)
        self.assertEqual(tag["id"], "test-tag")

    def test_insert_category(self):
        """Test inserting a category"""
        category_data = {
            "type": "categories",
            "id": "test-category-1",
            "attributes": {
                "name": "Test Category"
            },
            "relationships": {
                "parent": {
                    "data": None
                }
            }
        }

        self.db.insert_category(category_data)

        # Verify the category was inserted
        cursor = self.db.conn.execute("SELECT * FROM categories WHERE id = ?", ("test-category-1",))
        category = cursor.fetchone()
        self.assertIsNotNone(category)
        self.assertEqual(category["name"], "Test Category")
        self.assertIsNone(category["parent_id"])

    def test_insert_webhook(self):
        """Test inserting a webhook"""
        webhook_data = {
            "type": "webhooks",
            "id": "test-webhook-1",
            "attributes": {
                "url": "https://test.com/webhook",
                "description": "Test Webhook",
                "secret_key": "test-secret",
                "created_at": "2024-01-01T00:00:00+10:00"
            }
        }

        self.db.insert_webhook(webhook_data)

        # Verify the webhook was inserted
        cursor = self.db.conn.execute("SELECT * FROM webhooks WHERE id = ?", ("test-webhook-1",))
        webhook = cursor.fetchone()
        self.assertIsNotNone(webhook)
        self.assertEqual(webhook["url"], "https://test.com/webhook")
        self.assertEqual(webhook["description"], "Test Webhook")

    def test_insert_webhook_log(self):
        """Test inserting a webhook log"""
        # First insert a webhook
        webhook_data = {
            "type": "webhooks",
            "id": "test-webhook-1",
            "attributes": {
                "url": "https://test.com/webhook",
                "description": "Test Webhook",
                "secret_key": "test-secret",
                "created_at": "2024-01-01T00:00:00+10:00"
            }
        }
        self.db.insert_webhook(webhook_data)

        # Now insert a webhook log
        log_data = {
            "id": "test-log-1",
            "attributes": {
                "request_url": "https://test.com/webhook",
                "request_body": '{"test": "data"}',
                "response_status_code": 200,
                "response_body": '{"status": "ok"}',
                "created_at": "2024-01-01T12:00:00+10:00"
            }
        }

        self.db.insert_webhook_log("test-webhook-1", log_data)

        # Verify the webhook log was inserted
        cursor = self.db.conn.execute("SELECT * FROM webhook_logs WHERE id = ?", ("test-log-1",))
        log = cursor.fetchone()
        self.assertIsNotNone(log)
        self.assertEqual(log["webhook_id"], "test-webhook-1")
        self.assertEqual(log["response_status_code"], 200)

if __name__ == '__main__':
    unittest.main() 