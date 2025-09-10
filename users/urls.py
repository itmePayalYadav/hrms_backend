from django.urls import path
from .views import (
    RegisterView, VerifyOTPView, ResendOTPView,
    LoginView, LogoutView, ChangePasswordView,
    ForgotPasswordView, ResetPasswordView
)

app_name = "accounts" 

urlpatterns = [
    # ----------------------------
    # User Registration & Authentication
    # ----------------------------
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # ----------------------------
    # OTP Verification
    # ----------------------------
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend-otp"),

    # ----------------------------
    # Password Management
    # ----------------------------
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
]
