from django.conf import settings
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.permissions import SAFE_METHODS

class OTPThrottle(UserRateThrottle):
    """
    Throttle OTP requests to prevent abuse.
    Default: 20 OTP requests per hour per user.
    """
    scope = "otp"

    def get_rate(self):
        return getattr(settings, "OTP_THROTTLE_RATE", "20/hour")


class LoginThrottle(UserRateThrottle):
    """
    Throttle login attempts to prevent brute-force attacks.
    Default: 30 login requests per hour per user.
    """
    scope = "login"

    def get_rate(self):
        return getattr(settings, "LOGIN_THROTTLE_RATE", "30/hour")


class GeneralThrottle(UserRateThrottle):
    """
    General-purpose throttle for other API endpoints.
    Provides separate limits for safe and unsafe HTTP methods.
    """
    scope = "general"

    def get_rate(self):
        request = getattr(self, 'request', None)
        if request and request.method in SAFE_METHODS:
            return getattr(settings, "GENERAL_THROTTLE_SAFE_RATE", "200/hour")
        return getattr(settings, "GENERAL_THROTTLE_UNSAFE_RATE", "50/hour")
