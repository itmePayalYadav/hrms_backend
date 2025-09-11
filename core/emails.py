import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings


class SendGridBackend(BaseEmailBackend):
    """
    Django email backend for SendGrid API.
    Usage:
        python manage.py shell
        from django.core.mail import send_mail
        send_mail("Subject", "Body", settings.EMAIL_FROM, ["recipient@example.com"])
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(settings, "SENDGRID_API_KEY") or not settings.SENDGRID_API_KEY:
            raise ValueError("SENDGRID_API_KEY is not set in settings.")
        self.sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        self.from_email = getattr(settings, "EMAIL_FROM", None)
        if not self.from_email:
            raise ValueError("EMAIL_FROM is not set in settings.")

    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of emails sent.
        """
        num_sent = 0
        for message in email_messages:
            try:
                mail = Mail(
                    from_email=Email(self.from_email),
                    to_emails=[To(addr) for addr in message.to],
                    subject=message.subject,
                    plain_text_content=Content("text/plain", message.body)
                )
                response = self.sg.send(mail)
                if 200 <= response.status_code < 300:
                    num_sent += 1
            except Exception as e:
                if not self.fail_silently:
                    raise e
        return num_sent
