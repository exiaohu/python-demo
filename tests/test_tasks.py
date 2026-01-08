from unittest.mock import patch

from app.tasks.email import send_email_task


def test_send_email_task() -> None:
    email_to = "test@example.com"
    subject = "Test Email"
    body = "This is a test email."

    with patch("time.sleep"):  # Mock sleep to speed up test
        result = send_email_task(email_to, subject, body)

    assert result == {"status": "sent", "email": email_to}
