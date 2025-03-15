# UP Bank Python Client

A Python client library for interacting with the UP Bank API. This library provides a clean, typed interface to all UP Bank API endpoints with full Pydantic model support.

## Installation

```bash
pip install upbank
```

## Features

- ✨ Complete UP Bank API v1 coverage
- 🔒 Type-safe request and response handling with Pydantic
- 📝 Comprehensive documentation and examples
- ✅ Extensive test coverage
- 🐍 Python 3.8+ support

## Quick Start

```python
from upbank import UpClient

# Initialize the client with your API key
client = UpClient("your_api_key")

# Get all accounts
accounts = client.get_accounts()
for account in accounts.data:
    print(f"Account: {account.attributes.display_name}")
    print(f"Balance: {account.attributes.balance.value} {account.attributes.balance.currency_code}")

# Get a specific transaction
transaction = client.get_transaction("transaction-id")
print(f"Transaction: {transaction.attributes.description}")
print(f"Amount: {transaction.attributes.amount.value}")
```

## Library Structure

```
upbank/
├── __init__.py          # Package initialization
├── client.py            # Main UpClient implementation
└── models/              # Pydantic models
    ├── __init__.py     # Models initialization
    ├── account.py      # Account models
    ├── base.py         # Base models and utilities
    ├── category.py     # Category models
    ├── tag.py          # Tag models
    ├── transaction.py  # Transaction models
    └── webhook.py      # Webhook models
```

## API Coverage

### Utility
```python
# Check API connectivity
ping = client.ping()
print(f"API Status: {ping['meta']['statusEmoji']}")
```

### Accounts
```python
# List all accounts (both methods are equivalent)
accounts = client.list_accounts()
accounts = client.get_accounts()  # alias

# Get a specific account
account = client.get_account("account-id")
```

### Transactions
```python
# List all transactions with optional filters (both methods are equivalent)
transactions = client.list_transactions(
    page_size=50,
    status="SETTLED",
    since="2024-01-01T00:00:00+10:00",
    category="category-id",
    tag="tag-id"
)
transactions = client.get_transactions()  # alias with same parameters

# Get a specific transaction
transaction = client.get_transaction("transaction-id")

# Update transaction category
client.update_transaction_category("transaction-id", "category-id")
# Remove transaction category
client.update_transaction_category("transaction-id", None)

# Add tags to a transaction
client.add_tags_to_transaction("transaction-id", ["tag1", "tag2"])

# Remove tags from a transaction
client.remove_tags_from_transaction("transaction-id", ["tag1", "tag2"])
```

### Categories
```python
# List all categories (both methods are equivalent)
categories = client.list_categories()
categories = client.get_categories()  # alias

# List categories with parent filter
categories = client.list_categories(parent="parent-category-id")

# Get a specific category
category = client.get_category("category-id")
```

### Tags
```python
# List all tags
tags = client.list_tags()
```

### Webhooks
```python
# List all webhooks (both methods are equivalent)
webhooks = client.list_webhooks()
webhooks = client.get_webhooks()  # alias

# Create a new webhook
webhook = client.create_webhook(
    url="https://your-webhook-url.com",
    description="My webhook"
)

# Get a specific webhook
webhook = client.get_webhook("webhook-id")

# Delete a webhook
client.delete_webhook("webhook-id")

# List webhook logs
logs = client.list_webhook_logs("webhook-id")
```

## Development

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/upbank-python.git
cd upbank-python
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements.txt
```

### Running Tests

The library uses pytest for testing. To run the tests:

```bash
# Run all tests
python -m pytest tests/ -v

# Run tests with coverage report
pytest --cov=upbank

# Run specific test file
pytest tests/test_client.py

# Run tests matching a pattern
pytest -k "test_account"


```

### Test Structure

```
tests/
├── conftest.py         # Test fixtures and configuration
├── test_client.py      # Client tests
└── test_models.py      # Model tests
```

The test suite includes:
- Unit tests for all API endpoints
- Model validation tests
- Error handling tests
- Mock request/response handling
- Comprehensive fixtures for testing

## Model Structure

### Base Models
- `MoneyObject`: Represents currency amounts with currency code and value
- `Links`: Handles API navigation links (self, related, prev, next)
- `Relationship`: Represents relationships between resources
- `PaginatedResponse`: Base class for paginated API responses

### Resource Models
- `Account`: Banking account details
- `Transaction`: Transaction records with amounts and metadata
- `Category`: Transaction categorization
- `Tag`: Transaction tagging
- `Webhook`: Webhook configuration and logs

Each resource model includes:
- Type-safe attributes
- Relationship handling
- Validation rules
- JSON serialization/deserialization

## Error Handling

The client handles various error cases:
- HTTP errors (4xx, 5xx)
- Validation errors
- Authentication errors
- Rate limiting

Example error handling:

```python
from requests.exceptions import HTTPError

try:
    account = client.get_account("invalid-id")
except HTTPError as e:
    if e.response.status_code == 404:
        print("Account not found")
    elif e.response.status_code == 401:
        print("Invalid API key")
    else:
        print(f"API error: {e}")
```

## License

MIT License 