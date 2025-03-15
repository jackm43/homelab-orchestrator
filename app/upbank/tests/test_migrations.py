"""
Tests for UP Bank database migrations
"""

import os
import sqlite3
import unittest
from upbank.migrations import init_db

class TestMigrations(unittest.TestCase):
    def setUp(self):
        """Set up test database"""
        self.test_db_path = "test_migrations.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_migrations(self):
        """Test that migrations create the expected schema"""
        # Run migrations
        init_db(self.test_db_path)

        # Connect to database and verify schema
        conn = sqlite3.connect(self.test_db_path)
        try:
            # Enable foreign key support for this connection
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()

            # Check that migrations table exists and has our migration
            cursor.execute("SELECT id FROM migrations")
            migrations = cursor.fetchall()
            self.assertEqual(len(migrations), 1)
            self.assertEqual(migrations[0][0], "0001_initial_schema")

            # Check that all tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            expected_tables = [
                'accounts',
                'categories',
                'migrations',
                'tags',
                'transaction_tags',
                'transactions',
                'webhook_logs',
                'webhooks'
            ]
            self.assertEqual(sorted(tables), expected_tables)

            # Check that indexes exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name LIKE 'idx_%'
                ORDER BY name
            """)
            indexes = [row[0] for row in cursor.fetchall()]
            expected_indexes = [
                'idx_categories_parent_id',
                'idx_transactions_account_id',
                'idx_transactions_category_id',
                'idx_transactions_created_at',
                'idx_webhook_logs_webhook_id'
            ]
            self.assertEqual(sorted(indexes), expected_indexes)

            # Verify foreign key constraints are enabled
            cursor.execute("PRAGMA foreign_keys")
            self.assertEqual(cursor.fetchone()[0], 1)

            # Test idempotency - running migrations again should not error
            init_db(self.test_db_path)
            cursor.execute("SELECT COUNT(*) FROM migrations")
            migration_count = cursor.fetchone()[0]
            self.assertEqual(migration_count, 1)

        finally:
            conn.close()

if __name__ == '__main__':
    unittest.main() 