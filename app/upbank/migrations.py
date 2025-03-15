"""
Database migrations for UP Bank SQLite database
"""

import sqlite3
from pathlib import Path
from typing import List, Tuple

MIGRATIONS: List[Tuple[str, str]] = [
    ("0001_initial_schema", """
        -- Create migrations table to track applied migrations
        CREATE TABLE IF NOT EXISTS migrations (
            id TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Accounts table
        CREATE TABLE IF NOT EXISTS accounts (
            id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            account_type TEXT NOT NULL,
            ownership_type TEXT NOT NULL,
            balance_currency_code TEXT NOT NULL,
            balance_value TEXT NOT NULL,
            balance_value_in_base_units INTEGER NOT NULL,
            created_at TEXT NOT NULL
        );

        -- Transactions table
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            status TEXT NOT NULL,
            raw_text TEXT,
            description TEXT NOT NULL,
            message TEXT,
            is_categorizable BOOLEAN NOT NULL,
            amount_currency_code TEXT NOT NULL,
            amount_value TEXT NOT NULL,
            amount_value_in_base_units INTEGER NOT NULL,
            foreign_amount_currency_code TEXT,
            foreign_amount_value TEXT,
            foreign_amount_value_in_base_units INTEGER,
            settled_at TEXT,
            created_at TEXT NOT NULL,
            transaction_type TEXT,
            note TEXT,
            note_created_at TEXT,
            category_id TEXT,
            transfer_account_id TEXT,
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (transfer_account_id) REFERENCES accounts(id)
        );

        -- Categories table
        CREATE TABLE IF NOT EXISTS categories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            parent_id TEXT,
            FOREIGN KEY (parent_id) REFERENCES categories(id)
        );

        -- Tags table
        CREATE TABLE IF NOT EXISTS tags (
            id TEXT PRIMARY KEY
        );

        -- Transaction Tags (junction table)
        CREATE TABLE IF NOT EXISTS transaction_tags (
            transaction_id TEXT,
            tag_id TEXT,
            PRIMARY KEY (transaction_id, tag_id),
            FOREIGN KEY (transaction_id) REFERENCES transactions(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id)
        );

        -- Webhooks table
        CREATE TABLE IF NOT EXISTS webhooks (
            id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            description TEXT,
            secret_key TEXT,
            created_at TEXT NOT NULL
        );

        -- Webhook Logs table
        CREATE TABLE IF NOT EXISTS webhook_logs (
            id TEXT PRIMARY KEY,
            webhook_id TEXT NOT NULL,
            request_url TEXT NOT NULL,
            request_body TEXT,
            response_status_code INTEGER,
            response_body TEXT,
            delivery_status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (webhook_id) REFERENCES webhooks(id)
        );

        -- Create indexes for better query performance
        CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_category_id ON transactions(category_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
        CREATE INDEX IF NOT EXISTS idx_webhook_logs_webhook_id ON webhook_logs(webhook_id);
        CREATE INDEX IF NOT EXISTS idx_categories_parent_id ON categories(parent_id);
    """),
]

def init_db(db_path: str) -> None:
    """Initialize the database and run migrations"""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id TEXT PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        for migration_id, migration_sql in MIGRATIONS:
            cursor = conn.execute(
                "SELECT id FROM migrations WHERE id = ?", 
                (migration_id,)
            )
            if cursor.fetchone() is None:
                conn.executescript(migration_sql)
                conn.execute(
                    "INSERT INTO migrations (id) VALUES (?)",
                    (migration_id,)
                )
                conn.commit()
                print(f"Applied migration: {migration_id}")
            else:
                print(f"Skipping migration {migration_id} (already applied)")

    except sqlite3.Error as e:
        print(f"Error applying migrations: {e}")
        raise
    finally:
        conn.close()

def main():
    """Main entry point for running migrations"""
    import os
    import argparse

    parser = argparse.ArgumentParser(description="UP Bank database migrations")
    parser.add_argument(
        "--db-path",
        default=os.environ.get("UPBANK_DB_PATH", "upbank.db"),
        help="Path to SQLite database (default: upbank.db or UPBANK_DB_PATH env var)"
    )
    args = parser.parse_args()

    print(f"Initializing database at: {args.db_path}")
    init_db(args.db_path)
    print("Database initialization complete")

if __name__ == "__main__":
    main() 