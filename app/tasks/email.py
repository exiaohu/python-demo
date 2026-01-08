import time
from typing import Dict

from celery import shared_task  # type: ignore

from app.core.logger import logger


@shared_task  # type: ignore
def send_email_task(email_to: str, subject: str, body: str) -> Dict[str, str]:
    """
    Example background task to simulate sending an email.
    """
    logger.info(f"Starting email task for {email_to}")
    # Simulate IO delay
    time.sleep(2)
    logger.info(f"Email sent to {email_to} with subject '{subject}'")
    return {"status": "sent", "email": email_to}
