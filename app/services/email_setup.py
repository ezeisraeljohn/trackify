import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from app.core import settings


class EmailService:
    def __init__(self):
        self.smtp_server = settings.EMAIL_HOST
        self.smtp_port = int(settings.EMAIL_PORT)
        self.smtp_user = settings.EMAIL_USER
        self.smtp_password = settings.EMAIL_PASSWORD

    def _get_smtp_connection(self):
        if not self.smtp_server:
            raise ValueError("EMAIL_HOST not set")
        if self.smtp_port == 465:
            return smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
        else:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.ehlo()
            server.starttls()
            return server

    def send_email(self, to_email: str, subject: str, body: str) -> None:
        if not self.smtp_user:
            raise ValueError("EMAIL_USER not set")
        if not self.smtp_password:
            raise ValueError("EMAIL_PASSWORD not set")
        msg = MIMEMultipart()
        msg["From"] = formataddr(("Trackify Support", self.smtp_user))
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        try:
            with self._get_smtp_connection() as server:
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, to_email, msg.as_string())
            print(f"Email sent to {to_email}")
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")

    def send_batch_emails(self, emails: list, subject: str, body: str) -> None:
        for email in emails:
            self.send_email(email, subject, body)
        print(f"Batch email sent to {len(emails)} recipients.")
