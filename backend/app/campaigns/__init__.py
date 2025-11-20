"""
Email Campaign System
Direct outreach and email campaign management
"""

from typing import Dict, Any, List, Optional
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import asyncio
import logging
from datetime import datetime, timedelta
from jinja2 import Template

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailTemplate:
    """Email template with variable substitution"""

    def __init__(self, subject: str, body: str, template_type: str = "html"):
        """
        Initialize email template

        Args:
            subject: Email subject (supports variables)
            body: Email body (supports variables)
            template_type: 'html' or 'plain'
        """
        self.subject_template = Template(subject)
        self.body_template = Template(body)
        self.template_type = template_type

    def render(self, variables: Dict[str, Any]) -> Dict[str, str]:
        """
        Render template with variables

        Args:
            variables: Dictionary of template variables

        Returns:
            Dictionary with rendered subject and body
        """
        return {
            "subject": self.subject_template.render(**variables),
            "body": self.body_template.render(**variables),
            "type": self.template_type
        }


class EmailMessage:
    """Email message"""

    def __init__(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
        body_type: str = "html",
        attachments: Optional[List[Dict[str, Any]]] = None
    ):
        self.to_email = to_email
        self.subject = subject
        self.body = body
        self.from_email = from_email or settings.SMTP_FROM_EMAIL
        self.from_name = from_name or settings.SMTP_FROM_NAME
        self.reply_to = reply_to or self.from_email
        self.body_type = body_type
        self.attachments = attachments or []

    def to_mime(self) -> MIMEMultipart:
        """
        Convert to MIME message

        Returns:
            MIME message object
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = self.subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = self.to_email
        msg["Reply-To"] = self.reply_to

        # Add body
        if self.body_type == "html":
            part = MIMEText(self.body, "html")
        else:
            part = MIMEText(self.body, "plain")

        msg.attach(part)

        # Add attachments
        for attachment in self.attachments:
            self._attach_file(msg, attachment)

        return msg

    def _attach_file(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Attach file to message"""
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment["content"])
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {attachment['filename']}"
        )
        msg.attach(part)


class SMTPClient:
    """SMTP client for sending emails"""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD

    async def send(self, message: EmailMessage) -> Dict[str, Any]:
        """
        Send email via SMTP

        Args:
            message: Email message to send

        Returns:
            Send result
        """
        try:
            # Create MIME message
            mime_msg = message.to_mime()

            # Connect and send
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=False
            ) as smtp:
                # Start TLS
                await smtp.starttls()

                # Login
                if self.smtp_user and self.smtp_password:
                    await smtp.login(self.smtp_user, self.smtp_password)

                # Send message
                await smtp.send_message(mime_msg)

            logger.info(f"Email sent successfully to {message.to_email}")

            return {
                "success": True,
                "to_email": message.to_email,
                "subject": message.subject,
                "sent_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error sending email to {message.to_email}: {str(e)}")
            return {
                "success": False,
                "to_email": message.to_email,
                "error": str(e)
            }

    async def send_batch(
        self,
        messages: List[EmailMessage],
        rate_limit: int = 10,
        delay: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Send batch of emails with rate limiting

        Args:
            messages: List of email messages
            rate_limit: Max emails per batch
            delay: Delay between batches in seconds

        Returns:
            List of send results
        """
        results = []
        batches = [messages[i:i + rate_limit] for i in range(0, len(messages), rate_limit)]

        for batch_idx, batch in enumerate(batches):
            logger.info(f"Sending batch {batch_idx + 1}/{len(batches)} ({len(batch)} emails)")

            # Send batch concurrently
            tasks = [self.send(msg) for msg in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            results.extend(batch_results)

            # Delay between batches (except for last batch)
            if batch_idx < len(batches) - 1:
                await asyncio.sleep(delay)

        return results


class Campaign:
    """Email campaign"""

    def __init__(
        self,
        name: str,
        template: EmailTemplate,
        leads: List[Dict[str, Any]],
        schedule: Optional[datetime] = None,
        rate_limit: int = 10
    ):
        """
        Initialize campaign

        Args:
            name: Campaign name
            template: Email template
            leads: List of leads to email
            schedule: Optional scheduled send time
            rate_limit: Max emails per batch
        """
        self.name = name
        self.template = template
        self.leads = leads
        self.schedule = schedule
        self.rate_limit = rate_limit
        self.status = "draft"
        self.results: List[Dict[str, Any]] = []
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def prepare_messages(self) -> List[EmailMessage]:
        """
        Prepare email messages for all leads

        Returns:
            List of email messages
        """
        messages = []

        for lead in self.leads:
            # Prepare template variables
            variables = {
                "first_name": self._extract_first_name(lead.get("contact_name", "")),
                "last_name": self._extract_last_name(lead.get("contact_name", "")),
                "company_name": lead.get("company_name", ""),
                "contact_title": lead.get("contact_title", ""),
                "industry": lead.get("industry", ""),
                **lead  # Include all lead fields
            }

            # Render template
            rendered = self.template.render(variables)

            # Get email address
            to_email = lead.get("email") or lead.get("contact_email")

            if not to_email:
                logger.warning(f"No email for lead: {lead.get('company_name')}")
                continue

            # Create message
            message = EmailMessage(
                to_email=to_email,
                subject=rendered["subject"],
                body=rendered["body"],
                body_type=rendered["type"]
            )

            messages.append(message)

        logger.info(f"Prepared {len(messages)} messages for campaign: {self.name}")

        return messages

    def _extract_first_name(self, full_name: str) -> str:
        """Extract first name from full name"""
        if not full_name:
            return ""
        return full_name.split()[0]

    def _extract_last_name(self, full_name: str) -> str:
        """Extract last name from full name"""
        if not full_name:
            return ""
        parts = full_name.split()
        return parts[-1] if len(parts) > 1 else ""

    async def send(self, smtp_client: Optional[SMTPClient] = None) -> Dict[str, Any]:
        """
        Send campaign

        Args:
            smtp_client: Optional SMTP client (creates new if not provided)

        Returns:
            Campaign results
        """
        if self.status == "sent":
            raise ValueError("Campaign already sent")

        # Check schedule
        if self.schedule and datetime.utcnow() < self.schedule:
            raise ValueError(f"Campaign scheduled for {self.schedule}")

        self.status = "sending"
        self.started_at = datetime.utcnow()

        logger.info(f"Starting campaign: {self.name}")

        # Prepare messages
        messages = self.prepare_messages()

        # Send emails
        if smtp_client is None:
            smtp_client = SMTPClient()

        self.results = await smtp_client.send_batch(
            messages,
            rate_limit=self.rate_limit
        )

        # Update status
        self.status = "sent"
        self.completed_at = datetime.utcnow()

        # Calculate statistics
        success_count = sum(1 for r in self.results if r.get("success"))
        fail_count = len(self.results) - success_count

        logger.info(
            f"Campaign completed: {self.name} - "
            f"Sent: {success_count}, Failed: {fail_count}"
        )

        return {
            "campaign_name": self.name,
            "status": self.status,
            "total": len(self.results),
            "success": success_count,
            "failed": fail_count,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "duration_seconds": (self.completed_at - self.started_at).total_seconds(),
            "results": self.results
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get campaign statistics"""
        if not self.results:
            return {
                "status": self.status,
                "total": len(self.leads),
                "sent": 0,
                "failed": 0
            }

        success_count = sum(1 for r in self.results if r.get("success"))
        fail_count = len(self.results) - success_count

        return {
            "name": self.name,
            "status": self.status,
            "total": len(self.leads),
            "sent": success_count,
            "failed": fail_count,
            "success_rate": (success_count / len(self.results) * 100) if self.results else 0,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class CampaignManager:
    """
    Manages email campaigns

    Features:
    - Campaign creation and management
    - Template management
    - Scheduled sending
    - Analytics and tracking
    """

    def __init__(self):
        self.campaigns: Dict[str, Campaign] = {}
        self.templates: Dict[str, EmailTemplate] = {}
        self.smtp_client = SMTPClient()

    def create_template(self, name: str, subject: str, body: str, template_type: str = "html"):
        """Create email template"""
        template = EmailTemplate(subject, body, template_type)
        self.templates[name] = template
        logger.info(f"Created template: {name}")
        return template

    def get_template(self, name: str) -> Optional[EmailTemplate]:
        """Get template by name"""
        return self.templates.get(name)

    def create_campaign(
        self,
        name: str,
        template_name: str,
        leads: List[Dict[str, Any]],
        schedule: Optional[datetime] = None,
        rate_limit: int = 10
    ) -> Campaign:
        """
        Create email campaign

        Args:
            name: Campaign name
            template_name: Template name
            leads: List of leads
            schedule: Optional schedule time
            rate_limit: Max emails per batch

        Returns:
            Created campaign
        """
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")

        campaign = Campaign(
            name=name,
            template=template,
            leads=leads,
            schedule=schedule,
            rate_limit=rate_limit
        )

        self.campaigns[name] = campaign
        logger.info(f"Created campaign: {name} with {len(leads)} leads")

        return campaign

    async def send_campaign(self, name: str) -> Dict[str, Any]:
        """Send campaign by name"""
        campaign = self.campaigns.get(name)
        if not campaign:
            raise ValueError(f"Campaign not found: {name}")

        return await campaign.send(self.smtp_client)

    def get_campaign(self, name: str) -> Optional[Campaign]:
        """Get campaign by name"""
        return self.campaigns.get(name)

    def list_campaigns(self) -> List[Dict[str, Any]]:
        """List all campaigns"""
        return [campaign.get_stats() for campaign in self.campaigns.values()]

    async def send_scheduled_campaigns(self):
        """Send all scheduled campaigns that are due"""
        now = datetime.utcnow()
        sent_campaigns = []

        for name, campaign in self.campaigns.items():
            if campaign.status == "draft" and campaign.schedule and campaign.schedule <= now:
                logger.info(f"Sending scheduled campaign: {name}")
                try:
                    result = await campaign.send(self.smtp_client)
                    sent_campaigns.append(result)
                except Exception as e:
                    logger.error(f"Error sending scheduled campaign {name}: {str(e)}")

        return sent_campaigns


# Global campaign manager instance
campaign_manager = CampaignManager()


# Pre-built email templates
DEFAULT_TEMPLATES = {
    "intro": EmailTemplate(
        subject="Quick question about {{ company_name }}",
        body="""
        <html>
        <body>
            <p>Hi {{ first_name }},</p>

            <p>I noticed {{ company_name }} is in the {{ industry }} industry, and I thought you might be interested in our services.</p>

            <p>We specialize in helping companies like yours with digital marketing and lead generation.</p>

            <p>Would you be open to a quick 15-minute call to discuss how we can help {{ company_name }} grow?</p>

            <p>Best regards,<br>
            {{ sender_name }}</p>
        </body>
        </html>
        """,
        template_type="html"
    ),

    "follow_up": EmailTemplate(
        subject="Following up - {{ company_name }}",
        body="""
        <html>
        <body>
            <p>Hi {{ first_name }},</p>

            <p>I wanted to follow up on my previous email about helping {{ company_name }} with digital marketing.</p>

            <p>I have some ideas specific to the {{ industry }} industry that I think would be valuable for you.</p>

            <p>Are you available for a brief call this week?</p>

            <p>Thanks,<br>
            {{ sender_name }}</p>
        </body>
        </html>
        """,
        template_type="html"
    )
}

# Register default templates
for template_name, template in DEFAULT_TEMPLATES.items():
    campaign_manager.templates[template_name] = template
