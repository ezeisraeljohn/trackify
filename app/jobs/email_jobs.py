from app.celery_app import celery_app
from app.services.email_setup import EmailService
from app.utils.email_utils import render_email_template


@celery_app.task(name="send_confirmation_email")
def send_verification_email(email: str, subject: str, body: dict) -> None:
    """
    Send a confirmation email to the user.
    """
    email_service = EmailService()
    try:
        html_content = render_email_template("verify_email", {**body})
        email_service.send_email(
            to_email=email,
            subject=subject,
            body=html_content,
        )
    except Exception as e:
        print(f"Failed to send verification email to {email}: {e}")
