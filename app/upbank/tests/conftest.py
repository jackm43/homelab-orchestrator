"""
Pytest configuration and fixtures
"""

import json
from typing import Dict, Optional
from unittest.mock import MagicMock, patch

import pytest
import requests

from upbank import UpClient

class MockResponse:
    def __init__(self, status_code: int, json_data: Optional[Dict] = None, content: bytes = b""):
        self.status_code = status_code
        self._json_data = json_data
        self.content = content

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"HTTP Error: {self.status_code}")

@pytest.fixture
def mock_response():
    """Factory fixture to create mock responses"""
    def _mock_response(status_code: int = 200, json_data: Optional[Dict] = None, content: bytes = b""):
        return MockResponse(status_code, json_data, content)
    return _mock_response

@pytest.fixture
def mock_session():
    """Mock requests.Session"""
    with patch("requests.Session") as mock:
        session = MagicMock()
        mock.return_value = session
        yield session

@pytest.fixture
def client(mock_session):
    """Create an UpClient instance with a mocked session"""
    return UpClient("test_api_key")

@pytest.fixture
def account_response():
    """Account response fixture"""
    return {
        "data": {
            "type": "accounts",
            "id": "test-account-id",
            "attributes": {
                "displayName": "Test Account",
                "accountType": "SAVER",
                "ownershipType": "INDIVIDUAL",
                "balance": {
                    "currencyCode": "AUD",
                    "value": "100.00",
                    "valueInBaseUnits": 10000
                },
                "createdAt": "2023-01-01T00:00:00+10:00"
            },
            "relationships": {
                "transactions": {
                    "links": {
                        "related": "https://api.up.com.au/api/v1/accounts/test-account-id/transactions"
                    }
                }
            },
            "links": {
                "self": "https://api.up.com.au/api/v1/accounts/test-account-id"
            }
        }
    }

@pytest.fixture
def transaction_response():
    """Transaction response fixture"""
    return {
        "data": {
            "type": "transactions",
            "id": "test-transaction-id",
            "attributes": {
                "status": "SETTLED",
                "rawText": "Test Transaction Raw",
                "description": "Test Transaction",
                "message": "Test message",
                "isCategorizable": True,
                "holdInfo": None,
                "roundUp": None,
                "cashback": None,
                "amount": {
                    "currencyCode": "AUD",
                    "value": "-10.00",
                    "valueInBaseUnits": -1000
                },
                "foreignAmount": None,
                "cardPurchaseMethod": {
                    "method": "CARD",
                    "deviceId": None
                },
                "settledAt": "2023-01-01T00:00:00+10:00",
                "createdAt": "2023-01-01T00:00:00+10:00",
                "transactionType": "Purchase",
                "note": None,
                "performingCustomer": None
            },
            "relationships": {
                "account": {
                    "data": {
                        "type": "accounts",
                        "id": "test-account-id"
                    },
                    "links": {
                        "related": "https://api.up.com.au/api/v1/accounts/test-account-id"
                    }
                },
                "transferAccount": {
                    "data": None,
                    "links": None
                },
                "category": {
                    "data": {
                        "type": "categories",
                        "id": "test-category-id"
                    },
                    "links": {
                        "related": "https://api.up.com.au/api/v1/categories/test-category-id"
                    }
                },
                "parentCategory": {
                    "data": None,
                    "links": None
                },
                "tags": {
                    "data": [],
                    "links": {
                        "self": "https://api.up.com.au/api/v1/transactions/test-transaction-id/relationships/tags"
                    }
                }
            },
            "links": {
                "self": "https://api.up.com.au/api/v1/transactions/test-transaction-id"
            }
        }
    }

@pytest.fixture
def category_response():
    """Category response fixture"""
    return {
        "data": {
            "type": "categories",
            "id": "test-category-id",
            "attributes": {
                "name": "Test Category"
            },
            "relationships": {
                "parent": {
                    "data": None,
                    "links": {
                        "related": None
                    }
                },
                "children": {
                    "data": [],
                    "links": {
                        "related": "https://api.up.com.au/api/v1/categories/test-category-id/children"
                    }
                }
            },
            "links": {
                "self": "https://api.up.com.au/api/v1/categories/test-category-id"
            }
        }
    }

@pytest.fixture
def webhook_response():
    """Webhook response fixture"""
    return {
        "data": {
            "type": "webhooks",
            "id": "test-webhook-id",
            "attributes": {
                "url": "https://example.com/webhook",
                "description": "Test Webhook",
                "secretKey": "test-secret-key",
                "createdAt": "2023-01-01T00:00:00+10:00"
            },
            "relationships": {
                "logs": {
                    "links": {
                        "related": "https://api.up.com.au/api/v1/webhooks/test-webhook-id/logs"
                    }
                }
            },
            "links": {
                "self": "https://api.up.com.au/api/v1/webhooks/test-webhook-id"
            }
        }
    } 