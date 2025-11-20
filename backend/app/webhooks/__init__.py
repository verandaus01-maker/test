"""
Webhook System
Real-time event notifications via webhooks
"""

from typing import Dict, Any, List, Optional
import aiohttp
import asyncio
import hmac
import hashlib
import json
import logging
from datetime import datetime
from enum import Enum

from app.core.config import settings

logger = logging.getLogger(__name__)


class WebhookEvent(str, Enum):
    """Webhook event types"""
    # Lead events
    LEAD_CREATED = "lead.created"
    LEAD_UPDATED = "lead.updated"
    LEAD_ENRICHED = "lead.enriched"
    LEAD_SCORED = "lead.scored"
    LEAD_DELETED = "lead.deleted"

    # Job events
    JOB_STARTED = "job.started"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    JOB_PROGRESS = "job.progress"

    # Export events
    EXPORT_STARTED = "export.started"
    EXPORT_COMPLETED = "export.completed"
    EXPORT_FAILED = "export.failed"

    # Integration events
    CRM_SYNC_SUCCESS = "crm.sync.success"
    CRM_SYNC_FAILED = "crm.sync.failed"


class WebhookPayload:
    """Webhook payload structure"""

    def __init__(
        self,
        event: WebhookEvent,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ):
        self.event = event
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()
        self.webhook_id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique webhook ID"""
        import uuid
        return str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "webhook_id": self.webhook_id,
            "event": self.event.value if isinstance(self.event, WebhookEvent) else self.event,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


class WebhookDelivery:
    """Handles webhook delivery with retries"""

    def __init__(
        self,
        url: str,
        payload: WebhookPayload,
        secret: Optional[str] = None,
        max_retries: int = 3
    ):
        self.url = url
        self.payload = payload
        self.secret = secret or settings.WEBHOOK_SECRET
        self.max_retries = max_retries
        self.attempt = 0

    def _generate_signature(self, payload_json: str) -> str:
        """
        Generate HMAC signature for webhook verification

        Args:
            payload_json: JSON payload string

        Returns:
            Signature string
        """
        if not self.secret:
            return ""

        signature = hmac.new(
            self.secret.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    async def deliver(self) -> Dict[str, Any]:
        """
        Deliver webhook with retries

        Returns:
            Delivery result
        """
        payload_json = self.payload.to_json()
        signature = self._generate_signature(payload_json)

        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"LeadScraper-Webhook/1.0",
            "X-Webhook-Signature": f"sha256={signature}",
            "X-Webhook-Event": self.payload.event.value if isinstance(self.payload.event, WebhookEvent) else self.payload.event,
            "X-Webhook-ID": self.payload.webhook_id,
            "X-Webhook-Timestamp": str(int(self.payload.timestamp.timestamp()))
        }

        last_error = None

        for attempt in range(self.max_retries):
            self.attempt = attempt + 1

            try:
                timeout = aiohttp.ClientTimeout(total=settings.WEBHOOK_TIMEOUT)

                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        self.url,
                        data=payload_json,
                        headers=headers
                    ) as response:
                        response_text = await response.text()

                        if response.status in [200, 201, 202, 204]:
                            logger.info(
                                f"Webhook delivered successfully to {self.url} "
                                f"(attempt {self.attempt}/{self.max_retries})"
                            )
                            return {
                                "success": True,
                                "status_code": response.status,
                                "response": response_text,
                                "attempt": self.attempt
                            }
                        else:
                            last_error = f"HTTP {response.status}: {response_text}"
                            logger.warning(
                                f"Webhook delivery failed: {last_error} "
                                f"(attempt {self.attempt}/{self.max_retries})"
                            )

            except asyncio.TimeoutError:
                last_error = "Request timeout"
                logger.warning(
                    f"Webhook delivery timeout to {self.url} "
                    f"(attempt {self.attempt}/{self.max_retries})"
                )

            except Exception as e:
                last_error = str(e)
                logger.error(
                    f"Webhook delivery error: {last_error} "
                    f"(attempt {self.attempt}/{self.max_retries})"
                )

            # Wait before retry (exponential backoff)
            if self.attempt < self.max_retries:
                wait_time = 2 ** self.attempt  # 2, 4, 8 seconds
                await asyncio.sleep(wait_time)

        # All retries failed
        logger.error(
            f"Webhook delivery failed after {self.max_retries} attempts to {self.url}: "
            f"{last_error}"
        )

        return {
            "success": False,
            "error": last_error,
            "attempt": self.attempt
        }


class WebhookManager:
    """
    Manages webhook subscriptions and deliveries

    Features:
    - Event subscription
    - Webhook delivery with retries
    - Signature verification
    - Delivery logging
    """

    def __init__(self):
        self.subscriptions: Dict[str, List[str]] = {}
        self.delivery_log: List[Dict[str, Any]] = []

    def subscribe(self, event: WebhookEvent, url: str):
        """
        Subscribe to webhook event

        Args:
            event: Event type
            url: Webhook URL
        """
        event_name = event.value if isinstance(event, WebhookEvent) else event

        if event_name not in self.subscriptions:
            self.subscriptions[event_name] = []

        if url not in self.subscriptions[event_name]:
            self.subscriptions[event_name].append(url)
            logger.info(f"Subscribed {url} to {event_name}")

    def unsubscribe(self, event: WebhookEvent, url: str):
        """
        Unsubscribe from webhook event

        Args:
            event: Event type
            url: Webhook URL
        """
        event_name = event.value if isinstance(event, WebhookEvent) else event

        if event_name in self.subscriptions and url in self.subscriptions[event_name]:
            self.subscriptions[event_name].remove(url)
            logger.info(f"Unsubscribed {url} from {event_name}")

    def get_subscriptions(self, event: WebhookEvent) -> List[str]:
        """
        Get all URLs subscribed to an event

        Args:
            event: Event type

        Returns:
            List of webhook URLs
        """
        event_name = event.value if isinstance(event, WebhookEvent) else event
        return self.subscriptions.get(event_name, [])

    async def trigger(
        self,
        event: WebhookEvent,
        data: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Trigger webhook event

        Args:
            event: Event type
            data: Event data
            user_id: Optional user ID (for user-specific webhooks)

        Returns:
            List of delivery results
        """
        logger.info(f"Triggering webhook: {event.value if isinstance(event, WebhookEvent) else event}")

        # Get subscribed URLs
        urls = self.get_subscriptions(event)

        if not urls:
            logger.debug(f"No subscribers for event: {event}")
            return []

        # Create payload
        payload = WebhookPayload(event=event, data=data)

        # Deliver to all subscribers
        tasks = []
        for url in urls:
            delivery = WebhookDelivery(url=url, payload=payload)
            tasks.append(delivery.deliver())

        # Execute deliveries in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log results
        for url, result in zip(urls, results):
            log_entry = {
                "event": event.value if isinstance(event, WebhookEvent) else event,
                "url": url,
                "webhook_id": payload.webhook_id,
                "timestamp": payload.timestamp.isoformat(),
                "result": result if not isinstance(result, Exception) else {"error": str(result)},
                "user_id": user_id
            }
            self.delivery_log.append(log_entry)

        logger.info(f"Webhook triggered: {len(results)} deliveries attempted")

        return results

    def get_delivery_log(
        self,
        event: Optional[WebhookEvent] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get webhook delivery log

        Args:
            event: Optional event filter
            limit: Maximum number of entries

        Returns:
            List of log entries
        """
        log = self.delivery_log

        if event:
            event_name = event.value if isinstance(event, WebhookEvent) else event
            log = [entry for entry in log if entry['event'] == event_name]

        return log[-limit:]

    def clear_delivery_log(self):
        """Clear delivery log"""
        self.delivery_log.clear()
        logger.info("Webhook delivery log cleared")


# Global webhook manager instance
webhook_manager = WebhookManager()


# Helper functions for common webhook triggers
async def notify_lead_created(lead_data: Dict[str, Any], user_id: Optional[int] = None):
    """Send webhook notification for new lead"""
    await webhook_manager.trigger(WebhookEvent.LEAD_CREATED, lead_data, user_id)


async def notify_lead_enriched(lead_data: Dict[str, Any], user_id: Optional[int] = None):
    """Send webhook notification for enriched lead"""
    await webhook_manager.trigger(WebhookEvent.LEAD_ENRICHED, lead_data, user_id)


async def notify_job_completed(job_data: Dict[str, Any], user_id: Optional[int] = None):
    """Send webhook notification for completed job"""
    await webhook_manager.trigger(WebhookEvent.JOB_COMPLETED, job_data, user_id)


async def notify_export_completed(export_data: Dict[str, Any], user_id: Optional[int] = None):
    """Send webhook notification for completed export"""
    await webhook_manager.trigger(WebhookEvent.EXPORT_COMPLETED, export_data, user_id)
