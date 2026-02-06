"""
Email sending utilities for coaching reports.

Supports multiple email providers:
- SendGrid (recommended for production)
- AWS SES
- SMTP (generic)
- Console logging (for development)
"""

import logging
import os
from datetime import datetime
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from reports import TEMPLATES_DIR

logger = logging.getLogger(__name__)


def render_html_report(
    template_name: str,
    context: dict[str, Any],
) -> str:
    """
    Render HTML email template with context.

    Args:
        template_name: Name of template file (e.g., "weekly_report.html")
        context: Template variables

    Returns:
        Rendered HTML string
    """
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.get_template(template_name)
    return template.render(**context)


def send_email_sendgrid(
    to_email: str,
    subject: str,
    html_content: str,
    from_email: str = "coach@prefect.io",
) -> bool:
    """
    Send email via SendGrid.

    Requires SENDGRID_API_KEY environment variable.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email body
        from_email: Sender email address

    Returns:
        True if sent successfully, False otherwise
    """
    api_key = os.getenv("SENDGRID_API_KEY")

    if not api_key:
        logger.error("SENDGRID_API_KEY not configured")
        return False

    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )

        sg = SendGridAPIClient(api_key)
        response = sg.send(message)

        if response.status_code in (200, 201, 202):
            logger.info(f"Email sent successfully to {to_email} via SendGrid")
            return True
        else:
            logger.error(f"SendGrid API returned status {response.status_code}: {response.body}")
            return False

    except ImportError:
        logger.error("sendgrid package not installed. Install with: pip install sendgrid")
        return False
    except Exception as e:
        logger.error(f"Failed to send email via SendGrid: {e}", exc_info=True)
        return False


def send_email_ses(
    to_email: str,
    subject: str,
    html_content: str,
    from_email: str = "coach@prefect.io",
) -> bool:
    """
    Send email via AWS SES.

    Requires boto3 and AWS credentials configured.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email body
        from_email: Sender email address

    Returns:
        True if sent successfully, False otherwise
    """
    try:
        import boto3
        from botocore.exceptions import ClientError

        client = boto3.client("ses")

        response = client.send_email(
            Source=from_email,
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Html": {"Data": html_content}},
            },
        )

        logger.info(f"Email sent successfully to {to_email} via AWS SES")
        return True

    except ImportError:
        logger.error("boto3 package not installed. Install with: pip install boto3")
        return False
    except ClientError as e:
        logger.error(f"Failed to send email via AWS SES: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending via AWS SES: {e}", exc_info=True)
        return False


def send_email_smtp(
    to_email: str,
    subject: str,
    html_content: str,
    from_email: str = "coach@prefect.io",
) -> bool:
    """
    Send email via SMTP.

    Requires SMTP_* environment variables:
    - SMTP_HOST
    - SMTP_PORT
    - SMTP_USERNAME
    - SMTP_PASSWORD
    - SMTP_USE_TLS (optional, defaults to True)

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email body
        from_email: Sender email address

    Returns:
        True if sent successfully, False otherwise
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    if not all([host, username, password]):
        logger.error("SMTP credentials not fully configured")
        return False

    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email

        # Attach HTML
        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)

        # Send via SMTP
        with smtplib.SMTP(host, port) as server:
            if use_tls:
                server.starttls()
            server.login(username, password)
            server.send_message(msg)

        logger.info(f"Email sent successfully to {to_email} via SMTP")
        return True

    except Exception as e:
        logger.error(f"Failed to send email via SMTP: {e}", exc_info=True)
        return False


def send_email_console(
    to_email: str,
    subject: str,
    html_content: str,
    from_email: str = "coach@prefect.io",
) -> bool:
    """
    Log email to console (for development/testing).

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email body
        from_email: Sender email address

    Returns:
        True (always succeeds)
    """
    logger.info("=" * 80)
    logger.info("EMAIL (Console Mode)")
    logger.info("=" * 80)
    logger.info(f"From: {from_email}")
    logger.info(f"To: {to_email}")
    logger.info(f"Subject: {subject}")
    logger.info("-" * 80)
    logger.info(html_content[:500] + "..." if len(html_content) > 500 else html_content)
    logger.info("=" * 80)

    return True


def send_weekly_report_email(
    to_email: str,
    to_name: str,
    report_data: dict[str, Any],
    provider: str = "auto",
) -> bool:
    """
    Send weekly coaching report email.

    Args:
        to_email: Recipient email address
        to_name: Recipient name
        report_data: Report data dict with structure matching template
        provider: Email provider ("sendgrid", "ses", "smtp", "console", or "auto")

    Returns:
        True if sent successfully, False otherwise
    """
    # Determine provider
    if provider == "auto":
        if os.getenv("SENDGRID_API_KEY"):
            provider = "sendgrid"
        elif os.getenv("AWS_ACCESS_KEY_ID"):
            provider = "ses"
        elif os.getenv("SMTP_HOST"):
            provider = "smtp"
        else:
            logger.warning("No email provider configured, using console output")
            provider = "console"

    # Prepare template context
    context = {
        "rep_name": to_name,
        "week_start": report_data.get("week_start", ""),
        "total_calls": report_data.get("total_calls", 0),
        "total_sessions": report_data.get("total_sessions", 0),
        "overall_avg": report_data.get("overall_avg"),
        "overall_trend": report_data.get("overall_trend"),
        "dimensions": report_data.get("dimensions", []),
        "objections": report_data.get("objections", []),
        "calls": report_data.get("calls", []),
        "action_items": report_data.get("action_items", []),
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    }

    # Render HTML
    try:
        html_content = render_html_report("weekly_report.html", context)
    except Exception as e:
        logger.error(f"Failed to render email template: {e}", exc_info=True)
        return False

    # Prepare subject
    week_start_str = report_data.get("week_start", "")
    subject = f"Weekly Coaching Report - Week of {week_start_str}"

    # Send via appropriate provider
    send_fn = {
        "sendgrid": send_email_sendgrid,
        "ses": send_email_ses,
        "smtp": send_email_smtp,
        "console": send_email_console,
    }.get(provider)

    if not send_fn:
        logger.error(f"Unknown email provider: {provider}")
        return False

    return send_fn(to_email, subject, html_content)
