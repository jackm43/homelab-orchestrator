"""
Sync data from UP Bank API to local SQLite database or CSV files
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Protocol, Dict, Any, List
from upbank.client import UpClient
from upbank.database import UpDatabase
import dotenv
import csv

dotenv.load_dotenv()

DEV_MODE = os.getenv('UPBANK_DEV_MODE', '').lower() in ('true', '1', 'yes')
if DEV_MODE:
    print("Running in development mode - data retrieval will be limited")

class DataHandler(Protocol):
    """Protocol for handling data output"""
    def insert_account(self, data: Dict[str, Any]) -> None:
        """Insert account data"""
        ...
    
    def insert_category(self, data: Dict[str, Any]) -> None:
        """Insert category data"""
        ...
    
    def insert_transaction(self, data: Dict[str, Any]) -> None:
        """Insert transaction data"""
        ...
    
    def insert_webhook(self, data: Dict[str, Any]) -> None:
        """Insert webhook data"""
        ...
    
    def insert_webhook_log(self, webhook_id: str, data: Dict[str, Any]) -> None:
        """Insert webhook log data"""
        ...

class DatabaseHandler:
    """Handler for database output"""
    def __init__(self, db_path: str):
        self.db = UpDatabase(db_path)
    
    def insert_account(self, data: Dict[str, Any]) -> None:
        self.db.insert_account(data)
    
    def insert_category(self, data: Dict[str, Any]) -> None:
        self.db.insert_category(data)
    
    def insert_transaction(self, data: Dict[str, Any]) -> None:
        self.db.insert_transaction(data)
    
    def insert_webhook(self, data: Dict[str, Any]) -> None:
        self.db.insert_webhook(data)
    
    def insert_webhook_log(self, webhook_id: str, data: Dict[str, Any]) -> None:
        self.db.insert_webhook_log(webhook_id, data)

class CsvHandler:
    """Handler for CSV output"""
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self._data: Dict[str, List[Dict[str, Any]]] = {
            'accounts': [],
            'categories': [],
            'transactions': [],
            'webhooks': [],
            'webhook_logs': []
        }
    
    @staticmethod
    def flatten_dict(d: dict, parent_key: str = '') -> dict:
        """Flatten a nested dictionary into a single level with underscore-separated keys"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}_{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(CsvHandler.flatten_dict(v, new_key).items())
            elif isinstance(v, (list, tuple)):
                if v and isinstance(v[0], dict):
                    for i, item in enumerate(v):
                        items.extend(CsvHandler.flatten_dict(item, f"{new_key}_{i}").items())
                else:
                    items.append((new_key, ','.join(map(str, v))))
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _write_csv(self, data_list: List[Dict[str, Any]], filename: str, extra_fields: Dict[str, Any] = None) -> None:
        if not data_list:
            return
            
        filepath = os.path.join(self.output_dir, filename)
        
        all_headers = set()
        for item in data_list:
            flattened = self.flatten_dict(item)
            all_headers.update(flattened.keys())
        
        if extra_fields:
            all_headers.update(extra_fields.keys())
        
        headers = sorted(all_headers)
            
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers, extrasaction='ignore')
            writer.writeheader()
            
            for item in data_list:
                row = self.flatten_dict(item)
                if extra_fields:
                    row = {**extra_fields, **row}
                for header in headers:
                    if header not in row:
                        row[header] = None
                writer.writerow(row)
    
    def insert_account(self, data: Dict[str, Any]) -> None:
        self._data['accounts'].append(data)
    
    def insert_category(self, data: Dict[str, Any]) -> None:
        self._data['categories'].append(data)
    
    def insert_transaction(self, data: Dict[str, Any]) -> None:
        self._data['transactions'].append(data)
    
    def insert_webhook(self, data: Dict[str, Any]) -> None:
        self._data['webhooks'].append(data)
    
    def insert_webhook_log(self, webhook_id: str, data: Dict[str, Any]) -> None:
        data['webhook_id'] = webhook_id  # Add webhook_id to the data
        self._data['webhook_logs'].append(data)
        
    def flush(self) -> None:
        """Write all collected data to CSV files"""
        for data_type, items in self._data.items():
            if items:
                self._write_csv(items, f"{data_type}.csv")
        self._data = {k: [] for k in self._data}

class UpBankSync:
    def __init__(self, api_key: str, handler: DataHandler):
        """
        Initialize sync with UP Bank API key and data handler
        
        Args:
            api_key: UP Bank API key
            handler: Handler for data output (database or CSV)
        """
        self.client = UpClient(api_key)
        self.handler = handler
        self.dev_mode = DEV_MODE

    def sync_accounts(self) -> None:
        """Sync all accounts from UP Bank"""
        print("Syncing accounts...")
        accounts = self.client.list_accounts()
        for account in accounts.data:
            self.handler.insert_account(account.model_dump())
        print(f"Synced {len(accounts.data)} accounts")

    def sync_categories(self) -> None:
        """Sync all categories from UP Bank"""
        print("Syncing categories...")
        categories = self.client.list_categories()
        for category in categories.data:
            self.handler.insert_category(category.model_dump())
        print(f"Synced {len(categories.data)} categories")

    def sync_transactions(
        self, 
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> None:
        """
        Sync transactions from UP Bank
        
        Args:
            since: Only get transactions since this date
            until: Only get transactions until this date
            status: Filter by transaction status (HELD or SETTLED)
        """
        print("Syncing transactions..." + (" (dev mode - limited to 1 page)" if self.dev_mode else ""))
        
        # Format dates for API
        since_str = since.isoformat() if since else None
        until_str = until.isoformat() if until else None
        
        transactions = self.client.list_transactions(
            since=since_str,
            until=until_str,
            status=status
        )
        
        count = 0
        while True:
            for transaction in transactions.data:
                self.handler.insert_transaction(transaction.model_dump())
                count += 1
            
            # Get next page if available and not in dev mode
            if transactions.links.next and not self.dev_mode:
                transactions = self.client.get_transactions(
                    since=since_str,
                    until=until_str,
                    status=status
                )
            else:
                break
        
        print(f"Synced {count} transactions")

    def sync_webhooks(self) -> None:
        """Sync all webhooks from UP Bank"""
        print("Syncing webhooks...")
        webhooks = self.client.list_webhooks()
        
        webhook_count = 0
        log_count = 0
        
        for webhook in webhooks.data:
            self.handler.insert_webhook(webhook.model_dump())
            webhook_count += 1
            
            logs = self.client.list_webhook_logs(webhook.id)
            for log in logs.data:
                self.handler.insert_webhook_log(webhook.id, log.model_dump())
                log_count += 1
                if self.dev_mode:
                    break
            
            if self.dev_mode:
                break
        
        print(f"Synced {webhook_count} webhooks with {log_count} logs" + 
              (" (limited by dev mode)" if self.dev_mode else ""))

    def sync_all(
        self,
        transaction_since: Optional[datetime] = None,
        transaction_until: Optional[datetime] = None,
        transaction_status: Optional[str] = None
    ) -> None:
        """
        Sync all data from UP Bank
        
        Args:
            transaction_since: Only get transactions since this date
            transaction_until: Only get transactions until this date
            transaction_status: Filter by transaction status (HELD or SETTLED)
        """
        self.sync_accounts()
        self.sync_categories()
        self.sync_transactions(
            since=transaction_since,
            until=transaction_until,
            status=transaction_status
        )
        self.sync_webhooks()
        
        if isinstance(self.handler, CsvHandler):
            self.handler.flush()

def main():
    """Main entry point for syncing data"""
    import questionary
    from datetime import datetime
    import os

    print("Welcome to UP Bank Data Sync Tool!")
    print("----------------------------------")
    
    if DEV_MODE:
        print("\n⚠️  Development mode enabled - data retrieval will be limited")
        print("   Set UPBANK_DEV_MODE=false to disable\n")

    api_key = os.environ.get("UP_API_KEY")
    if not api_key:
        api_key = questionary.text(
            "Enter your UP Bank API key:",
            validate=lambda text: len(text) > 0 or "API key cannot be empty"
        ).ask()

    if not api_key:
        print("API key is required. Exiting...")
        return

    output_type = questionary.select(
        "How would you like to save the data?",
        choices=[
            "CSV files (exports to separate files)",
            "SQLite database (all data in one file)"
        ]
    ).ask()

    is_csv = "CSV" in output_type

    if is_csv:
        default_path = "exports"
        csv_dir = questionary.text(
            "Enter directory for CSV files:",
            default=default_path
        ).ask()
        handler = CsvHandler(csv_dir)
    else:
        default_path = "up.db"
        db_path = questionary.text(
            "Enter path for SQLite database:",
            default=default_path
        ).ask()
        
        if not os.path.exists(db_path):
            should_init = questionary.confirm(
                "Database doesn't exist. Initialize it?",
                default=True
            ).ask()
            
            if should_init:
                from upbank.migrations import init_db
                print(f"Initializing database at: {db_path}")
                init_db(db_path)
        
        handler = DatabaseHandler(db_path)

    sync_types = questionary.checkbox(
        "What data would you like to sync?",
        choices=[
            questionary.Choice("All (syncs everything)", "all"),
            questionary.Choice("Accounts", "accounts"),
            questionary.Choice("Categories", "categories"),
            questionary.Choice("Transactions", "transactions"),
            questionary.Choice("Webhooks", "webhooks"),
        ],
        validate=lambda answers: len(answers) > 0 or "Please select at least one option"
    ).ask()

    transaction_filters = {}
    if "all" in sync_types or "transactions" in sync_types:
        if questionary.confirm("Would you like to filter transactions by date?").ask():
            date_format = "YYYY-MM-DD"
            since = questionary.text(
                f"Enter start date ({date_format}) or leave empty:",
                validate=lambda text: (
                    not text or 
                    (len(text.split('-')) == 3 and all(part.isdigit() for part in text.split('-')))
                )
            ).ask()
            
            until = questionary.text(
                f"Enter end date ({date_format}) or leave empty:",
                validate=lambda text: (
                    not text or 
                    (len(text.split('-')) == 3 and all(part.isdigit() for part in text.split('-')))
                )
            ).ask()

            if since:
                transaction_filters['since'] = datetime.fromisoformat(since)
            if until:
                transaction_filters['until'] = datetime.fromisoformat(until)

        if questionary.confirm("Would you like to filter transactions by status?").ask():
            status = questionary.select(
                "Select transaction status:",
                choices=["HELD", "SETTLED"]
            ).ask()
            transaction_filters['status'] = status

    sync = UpBankSync(api_key, handler)

    if "all" in sync_types:
        sync_types = ["accounts", "categories", "transactions", "webhooks"]
    
    try:
        for sync_type in sync_types:
            if sync_type == "transactions":
                sync.sync_transactions(**transaction_filters)
            elif sync_type == "accounts":
                sync.sync_accounts()
            elif sync_type == "categories":
                sync.sync_categories()
            elif sync_type == "webhooks":
                sync.sync_webhooks()
        
        if is_csv:
            handler.flush()
            print(f"\nData has been exported to: {os.path.abspath(csv_dir)}")
        else:
            print(f"\nData has been saved to: {os.path.abspath(db_path)}")
            
    except Exception as e:
        print(f"\nError during sync: {str(e)}")
        return

    print("\nSync completed successfully!")

if __name__ == "__main__":
    try:
        import questionary
    except ImportError:
        print("Please install required package: pip install questionary")
    else:
        main() 