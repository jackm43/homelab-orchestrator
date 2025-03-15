"""
Database operations for UP Bank data
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

class UpDatabase:
    def __init__(self, db_path: str = "upbank.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        """Create all necessary tables if they don't exist"""
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    account_type TEXT NOT NULL,
                    ownership_type TEXT NOT NULL,
                    balance_currency_code TEXT NOT NULL,
                    balance_value TEXT NOT NULL,
                    balance_value_in_base_units INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            self.conn.execute("""
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
                )
            """)

            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    parent_id TEXT,
                    FOREIGN KEY (parent_id) REFERENCES categories(id)
                )
            """)

            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id TEXT PRIMARY KEY
                )
            """)

            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS transaction_tags (
                    transaction_id TEXT,
                    tag_id TEXT,
                    PRIMARY KEY (transaction_id, tag_id),
                    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
                    FOREIGN KEY (tag_id) REFERENCES tags(id)
                )
            """)

            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS webhooks (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    description TEXT,
                    secret_key TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS webhook_logs (
                    id TEXT PRIMARY KEY,
                    webhook_id TEXT NOT NULL,
                    request_body TEXT NOT NULL,
                    response_status_code INTEGER,
                    response_body TEXT,
                    delivery_status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (webhook_id) REFERENCES webhooks(id)
                )
            """)

    def insert_account(self, account: Dict[str, Any]):
        """Insert or update an account"""
        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO accounts (
                    id, display_name, account_type, ownership_type,
                    balance_currency_code, balance_value, balance_value_in_base_units,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account["id"],
                account["attributes"]["display_name"],
                account["attributes"]["account_type"],
                account["attributes"]["ownership_type"],
                account["attributes"]["balance"]["currency_code"],
                account["attributes"]["balance"]["value"],
                account["attributes"]["balance"]["value_in_base_units"],
                account["attributes"]["created_at"]
            ))

    def insert_transaction(self, transaction: Dict[str, Any]):
        """Insert or update a transaction"""
        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO transactions (
                    id, account_id, status, raw_text, description, message,
                    is_categorizable, amount_currency_code, amount_value,
                    amount_value_in_base_units, foreign_amount_currency_code,
                    foreign_amount_value, foreign_amount_value_in_base_units,
                    settled_at, created_at, transaction_type, note, note_created_at,
                    category_id, transfer_account_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction["id"],
                transaction["relationships"]["account"]["data"]["id"],
                transaction["attributes"]["status"],
                transaction["attributes"].get("raw_text"),
                transaction["attributes"]["description"],
                transaction["attributes"].get("message"),
                transaction["attributes"]["is_categorizable"],
                transaction["attributes"]["amount"]["currency_code"],
                transaction["attributes"]["amount"]["value"],
                transaction["attributes"]["amount"]["value_in_base_units"],
                transaction["attributes"].get("foreign_amount", {}).get("currency_code") if transaction["attributes"].get("foreign_amount") else None,
                transaction["attributes"].get("foreign_amount", {}).get("value") if transaction["attributes"].get("foreign_amount") else None,
                transaction["attributes"].get("foreign_amount", {}).get("value_in_base_units") if transaction["attributes"].get("foreign_amount") else None,
                transaction["attributes"].get("settled_at"),
                transaction["attributes"]["created_at"],
                transaction["attributes"].get("transaction_type"),
                transaction["attributes"].get("note", {}).get("value") if transaction["attributes"].get("note") else None,
                transaction["attributes"].get("note", {}).get("created_at") if transaction["attributes"].get("note") else None,
                (transaction["relationships"].get("category", {}).get("data", {}) or {}).get("id"),
                (transaction["relationships"].get("transfer_account", {}).get("data", {}) or {}).get("id")
            ))

            if "tags" in transaction["relationships"] and transaction["relationships"]["tags"].get("data"):
                for tag in transaction["relationships"]["tags"]["data"]:
                    self.conn.execute("""
                        INSERT OR IGNORE INTO tags (id) VALUES (?)
                    """, (tag["id"],))
                    
                    self.conn.execute("""
                        INSERT OR IGNORE INTO transaction_tags (transaction_id, tag_id)
                        VALUES (?, ?)
                    """, (transaction["id"], tag["id"]))

    def insert_category(self, category: Dict[str, Any]):
        """Insert or update a category"""
        with self.conn:
            parent_data = category.get("relationships", {}).get("parent", {}).get("data")
            parent_id = parent_data.get("id") if parent_data is not None else None

            self.conn.execute("""
                INSERT OR REPLACE INTO categories (id, name, parent_id)
                VALUES (?, ?, ?)
            """, (
                category["id"],
                category["attributes"]["name"],
                parent_id
            ))

    def insert_webhook(self, webhook: Dict[str, Any]):
        """Insert or update a webhook"""
        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO webhooks (
                    id, url, description, secret_key, created_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                webhook["id"],
                webhook["attributes"]["url"],
                webhook["attributes"].get("description"),
                webhook["attributes"].get("secret_key"),
                webhook["attributes"]["created_at"]
            ))

    def insert_webhook_log(self, webhook_id: str, log: Dict[str, Any]):
        """Insert or update a webhook log"""
        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO webhook_logs (
                    id, webhook_id, request_body, response_status_code,
                    response_body, delivery_status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                log["id"],
                webhook_id,
                log["attributes"]["request"]["body"],
                log["attributes"]["response"]["status_code"] if log["attributes"].get("response") else None,
                log["attributes"]["response"]["body"] if log["attributes"].get("response") else None,
                log["attributes"]["delivery_status"],
                log["attributes"]["created_at"]
            ))

    def close(self):
        """Close the database connection"""
        self.conn.close() 