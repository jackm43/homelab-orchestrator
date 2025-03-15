import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import Dict

from immich_pyclient import Immich
from jellyfin_pyclient import JellyfinCollectionManager
from up_bank_pyclient import UpClient

app = FastAPI(
    title="API",
    version="1.0.0"
)

app.add_middleware( 
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """
    Root endpoint that returns API information.
    
    Returns:
        Dict[str, str]: A dictionary containing API status information.
    """
    return {"status": "API is running"}

# curl -X POST http://localhost:8000/scan
@app.post("/scan", response_model=Dict[str, str])
async def scan_library() -> Dict[str, str]:
    """
    Trigger an Immich library scan.
    
    Returns:
        Dict[str, str]: A dictionary containing the scan status.
    """
    
    try:
        immich = Immich()
        response = immich.scan_library()
        
        if response.status_code in (200, 201, 202, 204):
            return {"status": "success", "message": "Immich library scan initiated successfully"}
        else:
            return {
                "status": "error", 
                "message": f"Scan failed with status {response.status_code}: {response.text}"
            }
            
    except Exception as e:
        return {"status": "error", "message": f"Error triggering scan: {str(e)}"}

client = UpClient(api_key=os.getenv("UP_API_KEY"))

@app.get("/ping")
async def ping():
    """Check if the API is working"""
    return client.ping()

@app.get("/accounts")
async def list_accounts(page_size = None):
    """List all accounts"""
    return client.list_accounts(page_size=page_size)

@app.get("/accounts/{account_id}")
async def get_account(account_id):
    """Get a specific account"""
    try:
        return client.get_account(account_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/transactions")
async def list_transactions(
    page_size = None,
    status = None,
    since = None,
    until = None,
    category = None,
    tag = None
):
    """List all transactions with optional filters"""
    return client.list_transactions(
        page_size=page_size,
        status=status,
        since=since,
        until=until,
        category=category,
        tag=tag
    )

@app.get("/transactions/{transaction_id}")
async def get_transaction(transaction_id):
    """Get a specific transaction"""
    return client.get_transaction(transaction_id)

@app.get("/categories")
async def list_categories(parent = None):
    """List all categories"""
    return client.list_categories(parent=parent)

@app.get("/categories/{category_id}")
async def get_category(category_id):
    """Get a specific category"""
    return client.get_category(category_id)

@app.get("/tags")
async def list_tags(page_size = None):
    """List all tags"""
    return client.list_tags(page_size=page_size)

@app.post("/transactions/{transaction_id}/tags")
async def add_tags(transaction_id, tag_update):
    """Add tags to a transaction"""
    client.add_tags_to_transaction(transaction_id, tag_update.tags)
    return {"status": "success"}

@app.delete("/transactions/{transaction_id}/tags")
async def remove_tags(transaction_id, tag_update):
    """Remove tags from a transaction"""
    client.remove_tags_from_transaction(transaction_id, tag_update.tags)
    return {"status": "success"}

@app.patch("/transactions/{transaction_id}/category")
async def update_category(transaction_id, category_update):
    """Update or remove a transaction's category"""
    client.update_transaction_category(transaction_id, category_update.category_id)
    return {"status": "success"}

@app.get("/webhooks")
async def list_webhooks(page_size = None):
    """List all webhooks"""
    return client.list_webhooks(page_size=page_size)

@app.post("/webhooks")
async def create_webhook(webhook):
    """Create a new webhook"""
    return client.create_webhook(url=webhook.url, description=webhook.description)

@app.get("/webhooks/{webhook_id}")
async def get_webhook(webhook_id):
    """Get a specific webhook"""
    return client.get_webhook(webhook_id)

@app.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id):
    """Delete a webhook"""
    client.delete_webhook(webhook_id)
    return {"status": "success"}

@app.get("/webhooks/{webhook_id}/logs")
async def list_webhook_logs(webhook_id, page_size = None):
    """List logs for a specific webhook"""
    return client.list_webhook_logs(webhook_id, page_size=page_size)