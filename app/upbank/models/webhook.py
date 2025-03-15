"""
Models for UP Bank webhook resources
"""

from typing import Dict, List, Optional
from pydantic import Field

from upbank.models.base import Links, PaginatedResponse, Relationship, UpBaseModel

class WebhookAttributes(UpBaseModel):
    """Attributes of a webhook"""
    url: str
    description: Optional[str] = None
    secret_key: Optional[str] = None
    created_at: str

class WebhookRelationships(UpBaseModel):
    """Relationships for a webhook"""
    logs: Relationship

class Webhook(UpBaseModel):
    """Webhook resource"""
    type: str = "webhooks"
    id: str
    attributes: WebhookAttributes
    relationships: WebhookRelationships
    links: Links

class WebhookList(PaginatedResponse[Webhook]):
    """List of webhooks response"""
    pass

class WebhookLogRequest(UpBaseModel):
    """Request information in a webhook log"""
    body: str

class WebhookLogResponse(UpBaseModel):
    """Response information in a webhook log"""
    status_code: int
    body: str

class WebhookLogAttributes(UpBaseModel):
    """Attributes of a webhook log"""
    request: WebhookLogRequest
    response: Optional[WebhookLogResponse] = None
    delivery_status: str
    created_at: str

class WebhookLogRelationships(UpBaseModel):
    """Relationships for a webhook log"""
    webhook_event: Relationship

class WebhookLog(UpBaseModel):
    """Webhook log resource"""
    type: str = "webhook-logs"
    id: str
    attributes: WebhookLogAttributes
    relationships: WebhookLogRelationships
    links: Links

class WebhookLogList(PaginatedResponse[WebhookLog]):
    """List of webhook logs response"""
    pass 