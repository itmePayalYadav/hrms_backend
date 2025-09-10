from django.conf import settings
from rest_framework.throttling import UserRateThrottle

class OTPThrottle(UserRateThrottle):
    """
    Throttle class for OTP requests.

    Limits OTP generation per user to prevent abuse.
    Default rate: 5 OTP requests per hour.
    """
    scope = "otp"

    def get_rate(self):
        return getattr(settings, "OTP_THROTTLE_RATE", "5/hour")


class LoginThrottle(UserRateThrottle):
    """
    Throttle class for login requests.

    Limits login attempts per user to prevent brute-force attacks.
    Default rate: 10 login requests per hour.
    """
    scope = "login"

    def get_rate(self):
        return getattr(settings, "LOGIN_THROTTLE_RATE", "10/hour")


class GeneralThrottle(UserRateThrottle):
    """
    General-purpose throttle for most API endpoints.

    Provides different rates for SAFE_METHODS (GET, HEAD, OPTIONS)
    and unsafe methods (POST, PUT, PATCH, DELETE).
    """
    scope = "general"

    def get_rate(self):
        """
        Determine the rate limit based on request method.
        Falls back to settings if defined, otherwise uses defaults.
        """
        request = getattr(self, 'request', None)
        if request and request.method in SAFE_METHODS:
            return getattr(settings, "GENERAL_THROTTLE_SAFE_RATE", "100/hour")
        return getattr(settings, "GENERAL_THROTTLE_UNSAFE_RATE", "10/hour")

