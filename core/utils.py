import random
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status as drf_status
from typing import Any, Optional, Dict

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
    """
    Send OTP to the user's email.
    """
    subject = "Your HRMS OTP Verification Code"
    message = f"Your OTP code is: {otp}. It is valid for {validity_minutes} minutes."
    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, message, from_email, [to_email], fail_silently=False)


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
