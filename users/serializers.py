from .models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from core.utils import generate_otp, send_otp_email
import logging

logger = logging.getLogger(__name__)


# ----------------------------
# Register Serializer
# ----------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password], style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ["email", "password", "password_confirm", "em_role", "em_phone", "em_gender"]

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords don't match"})
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email": "User with this email already exists"})
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")

        # Create user
        user = User.objects.create_user(password=password, **validated_data)
        user.is_verified = False
        user.save(update_fields=["is_verified"])

        # Send OTP
        otp = generate_otp()
        user.set_otp(otp)
        try:
            send_otp_email(user.email, otp, validity_minutes=10)
            logger.info(f"OTP sent to {user.email}")
        except Exception as e:
            user.delete()
            logger.warning(f"Registration rollback: failed to send OTP to {user.email} - {str(e)}")
            raise serializers.ValidationError({"email": f"Failed to send OTP: {str(e)}"})

        return user


# ----------------------------
# Verify OTP Serializer
# ----------------------------
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        if not user.verify_otp(data["otp"]):
            raise serializers.ValidationError("Invalid or expired OTP")

        if not user.is_verified:
            user.is_verified = True
            user.save(update_fields=["is_verified"])

        return user


# ----------------------------
# Resend OTP Serializer
# ----------------------------
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            if user.is_verified:
                raise serializers.ValidationError("User is already verified")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist")

    def save(self):
        user = User.objects.get(email=self.validated_data["email"])
        otp = generate_otp()
        user.set_otp(otp)
        try:
            send_otp_email(user.email, otp, validity_minutes=10)
            logger.info(f"Resent OTP to {user.email}")
        except Exception as e:
            raise serializers.ValidationError({"email": f"Failed to resend OTP: {str(e)}"})
        return user


# ----------------------------
# Change Password Serializer
# ----------------------------
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not check_password(value, user.password):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "New passwords don't match"})
        return data

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


# ----------------------------
# JWT Token Serializer (with role)
# ----------------------------
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_verified:
            raise serializers.ValidationError("Please verify your email before login.")
        data.update({
            "email": self.user.email,
            "role": self.user.em_role,
            "user_id": str(self.user.id),
            "is_verified": self.user.is_verified
        })
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.em_role
        token["email"] = user.email
        token["user_id"] = str(user.id)
        return token


# ----------------------------
# Forgot Password Serializer
# ----------------------------
class ForgotPasswordOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist")

    def save(self):
        otp = generate_otp()
        token = self.user.set_reset_password_token() 
        self.user.set_otp(otp, reset=True)
        try:
            send_otp_email(self.user.email, otp, validity_minutes=10)
            logger.info(f"Password reset OTP sent to {self.user.email}")
        except Exception as e:
            self.user.clear_reset_password_token()
            raise serializers.ValidationError({"email": f"Failed to send OTP: {str(e)}"})
        return {
            "email": self.user.email,
            "token": token
        }


# ----------------------------
# Reset Password Serializer
# ----------------------------
class ResetPasswordOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            self.user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email")

        if not self.user.verify_otp(data["otp"], reset=True):
            raise serializers.ValidationError("Invalid or expired OTP")

        if not self.user.verify_reset_password_token(data["token"]):
            self.user.clear_otp()
            raise serializers.ValidationError("Invalid or expired reset token")

        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "Passwords do not match"})

        return data

    def save(self):
        self.user.set_password(self.validated_data["new_password"])
        self.user.clear_reset_password_token()
        self.user.save()
        return self.user
