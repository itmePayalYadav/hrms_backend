import random
import logging
from threading import Thread
from smtplib import SMTPException
from typing import Any, Optional, Dict

from django.core.mail import send_mail
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status as drf_status
from rest_framework import serializers

logger = logging.getLogger(__name__)

# ----------------------------
# OTP Generator
# ----------------------------
def generate_otp(length: int = 6) -> str:
    """
    Generate a numeric OTP of specified length.
    Default length is 6 digits.
    """
    if length <= 0:
        raise ValueError("OTP length must be positive.")
    start = 10 ** (length - 1)
    end = (10 ** length) - 1
    return str(random.randint(start, end))


# ----------------------------
# Synchronous OTP email sender
# ----------------------------
def _send_otp_email_sync(to_email: str, otp: str, validity_minutes: int = 10) -> None:
    """
    Internal function to send OTP synchronously.
    """
    subject = "Your HRMS OTP Verification Code"
    message = f"Your OTP code is: {otp}. It is valid for {validity_minutes} minutes."
    from_email = getattr(settings, "EMAIL_FROM", None)

    if not from_email:
        raise ValueError("EMAIL_FROM is not configured in settings.")

    try:
        send_mail(subject, message, from_email, [to_email], fail_silently=False)
        logger.info(f"OTP email sent successfully to {to_email}")
    except SMTPException as e:
        logger.error(f"Failed to send OTP to {to_email}: {str(e)}")
        raise serializers.ValidationError(
            {"email": "Failed to send OTP email. Please try again later."}
        )


# ----------------------------
# Asynchronous OTP email sender
# ----------------------------
def send_otp_email(to_email: str, otp: str, validity_minutes: int = 10) -> None:
    """
    Send OTP email asynchronously using a background thread.
    """
    Thread(
        target=_send_otp_email_sync,
        args=(to_email, otp, validity_minutes),
        daemon=True
    ).start()


# ----------------------------
# API Response Utility
# ----------------------------
def api_response(
    status_str: str = "success",
    message: Optional[str] = None,
    data: Optional[Any] = None,
    errors: Optional[Dict[str, Any]] = None,
    status_code: int = drf_status.HTTP_200_OK
) -> Response:
    """
    Standardized API response structure for DRF.
    """
    response = {
        "status": status_str,
        "message": message,
        "data": data,
        "errors": errors
    }
    response = {k: v for k, v in response.items() if v is not None}
    return Response(response, status=status_code)
