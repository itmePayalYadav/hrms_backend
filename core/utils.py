import random
import logging
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status as drf_status
from typing import Any, Optional, Dict

logger = logging.getLogger(__name__)

# ----------------------------
# OTP Utility
# ----------------------------
def generate_otp(length: int = 6) -> str:
    """
    Generate a numeric OTP of specified length.
    Default length is 6 digits.
    """
    if length <= 0:
        raise ValueError("OTP length must be a positive integer.")
    range_start = 10 ** (length - 1)
    range_end = (10 ** length) - 1
    return str(random.randint(range_start, range_end))


def send_otp_email(to_email: str, otp: str, validity_minutes: int = 10) -> None:
    from django.core.mail import send_mail
    from django.conf import settings
    from smtplib import SMTPException

    subject = "Your HRMS OTP Verification Code"
    message = f"Your OTP code is: {otp}. It is valid for {validity_minutes} minutes."
    from_email = getattr(settings, "EMAIL_HOST_USER", None)

    if not from_email:
        raise ValueError("EMAIL_HOST_USER is not configured in settings.")

    try:
        send_mail(subject, message, from_email, [to_email], fail_silently=False)
    except SMTPException as e:
        logger.error(f"Failed to send OTP to {to_email}: {str(e)}")
        raise serializers.ValidationError({"email": "Failed to send OTP email. Please try again later."})


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
