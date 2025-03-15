import csv
from pathlib import Path

class EnrichedTransactions:
    def __init__(self):
        base_dir = Path('exports')
        self.transactions_file = base_dir / 'transactions.csv'
        self.accounts_file = base_dir / 'accounts.csv'
        self.output_file = base_dir / 'transactions_enriched.csv'
        self.account_names = self.load_account_names()

        self.enrich_transactions()
        print(f"Enriched transactions written to {self.output_file}")
        

    def clean_value(self, v):
        """Clean a value by stripping whitespace if it's a string, or returning empty string if None."""
        if v is None or v == '':
            return ''
        return v.strip() if isinstance(v, str) else v

    def clean_key(self, k):
        """Clean a key by stripping whitespace if it's a string, or returning empty string if None."""
        if k is None:
            return ''
        return k.strip()

    def load_account_names(self):
        """Load account IDs and display names into a dictionary."""
        account_names = {}
        with open(self.accounts_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cleaned_row = {self.clean_key(k): self.clean_value(v) for k, v in row.items()}
                account_names[cleaned_row['id']] = cleaned_row['attributes_display_name']
        return account_names

    def enrich_transactions(self):
        """Add account display names to transactions based on transfer account ID."""
        with open(self.transactions_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = [self.clean_key(field) for field in reader.fieldnames or []]
            fieldnames.append('transfer_account_display_name')
            
            with open(self.output_file, 'w', newline='', encoding='utf-8') as out_f:
                writer = csv.DictWriter(out_f, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in reader:
                    cleaned_row = {self.clean_key(k): self.clean_value(v) for k, v in row.items() if k is not None}
                    transfer_account_id = self.clean_value(cleaned_row.get('relationships_transfer_account_data_id'))
                    if transfer_account_id:
                        cleaned_row['transfer_account_display_name'] = self.account_names.get(transfer_account_id, '')
                    else:
                        cleaned_row['transfer_account_display_name'] = ''
                    writer.writerow(cleaned_row)

if __name__ == '__main__':
    EnrichedTransactions() 