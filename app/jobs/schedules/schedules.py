from app.celery_app import celery_app
from app.crud import get_unverified_users
from app.services.email_setup import EmailService
from app.db.session import get_session
from app.utils.email_utils import render_email_template
from app.core import settings


@celery_app.task(name="send_email_verification_reminders")
def send_email_verification_reminders() -> None:
    """
    Send email reminders to unverified users.
    """

    try:
        email_service = EmailService()
        db = next(get_session())
        users = get_unverified_users(db=db)
        emails = [user.email for user in users if user.email]
        body = {}
        subject = "Reminder: Please Verify Your Email Address"
        body = {}

        html_content = render_email_template("email_verification_reminder", body)

        email_service.send_batch_emails(
            emails=emails,
            subject=subject,
            body=html_content,
        )
        print(f"Sent email reminders to {len(emails)} unverified users.")

    except Exception as e:
        if settings.ENV != "production":
            print(f"Error sending email reminders")
        else:
            print(f"Failed to send email reminders: {e}")
