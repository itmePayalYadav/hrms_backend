from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
import logging

from core.utils import api_response

from .throttles import OTPThrottle, LoginThrottle, GeneralThrottle
from .serializers import (
    RegisterSerializer, VerifyOTPSerializer, ResendOTPSerializer,
    ChangePasswordSerializer, MyTokenObtainPairSerializer,
    ForgotPasswordOTPSerializer, ResetPasswordOTPSerializer
)

logger = logging.getLogger(__name__)

# ----------------------------
# Register
# ----------------------------
class RegisterView(generics.CreateAPIView):
    """
    Register a new user and send OTP for email verification.
    Throttled using GeneralThrottle to prevent abuse.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    # throttle_classes = [GeneralThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info(f"User {user.email} registered successfully")
        return api_response(
            message="User created successfully. OTP sent to your email for verification",
            data={"email": user.email},
            status_code=status.HTTP_201_CREATED
        )

# ----------------------------
# Verify OTP
# ----------------------------
class VerifyOTPView(APIView):
    """
    Verify OTP sent to user's email.
    Throttled using OTPThrottle to prevent brute-force attempts.
    """
    permission_classes = [AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        logger.info(f"User {request.data.get('email')} verified OTP successfully")
        return api_response(message="Account verified successfully")


# ----------------------------
# Resend OTP
# ----------------------------
class ResendOTPView(APIView):
    """
    Resend OTP to user's email.
    Throttled using OTPThrottle: 5 requests per hour per user.
    """
    permission_classes = [AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request, *args, **kwargs):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"OTP resent to {request.data.get('email')}")
        return api_response(message="OTP resent successfully")


# ----------------------------
# Login
# ----------------------------
class LoginView(TokenObtainPairView):
    """
    Obtain JWT access and refresh tokens.
    Throttled using LoginThrottle to prevent brute-force login attempts.
    """
    serializer_class = MyTokenObtainPairSerializer
    throttle_classes = [LoginThrottle]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            logger.info(f"User {request.data.get('email')} logged in successfully")
        return response


# ----------------------------
# Logout
# ----------------------------
class LogoutView(APIView):
    """
    Logout user by blacklisting refresh token.
    Throttled using GeneralThrottle.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [GeneralThrottle]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return api_response(
                status_str="error",
                message="Refresh token required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f"User {request.user.email} logged out successfully")
            return api_response(
                message="Logged out successfully",
                status_code=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            logger.error(f"Logout error for user {request.user.email}: {str(e)}")
            return api_response(
                status_str="error",
                message="Invalid token",
                errors=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )


# ----------------------------
# Change Password
# ----------------------------
class ChangePasswordView(generics.UpdateAPIView):
    """
    Allow authenticated users to change their password.
    Throttled using GeneralThrottle.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [GeneralThrottle]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"User {request.user.email} changed password successfully")
        return api_response(message="Password changed successfully")


# ----------------------------
# Forgot Password
# ----------------------------
class ForgotPasswordView(APIView):
    """
    Send OTP for password reset to user's email.
    Throttled using GeneralThrottle.
    """
    permission_classes = [AllowAny]
    throttle_classes = [GeneralThrottle]

    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"Password reset OTP sent to {request.data.get('email')}")
        return api_response(message="OTP sent to email for password reset")


# ----------------------------
# Reset Password
# ----------------------------
class ResetPasswordView(APIView):
    """
    Reset password using OTP verification.
    Throttled using GeneralThrottle.
    """
    permission_classes = [AllowAny]
    throttle_classes = [GeneralThrottle]

    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"User {request.data.get('email')} reset password successfully")
        return api_response(message="Password reset successfully")
