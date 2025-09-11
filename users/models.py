import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.crypto import get_random_string
from .managers import UserManager, ActiveUserManager
from core.constants import ROLE_CHOICES, STATUS_CHOICES, GENDER_CHOICES, BLOOD_GROUP_CHOICES


# ----------------------------
# Custom User Model
# ----------------------------
class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for HRMS.
    Includes authentication, employee details, OTP handling,
    and password reset token support.
    """

    # ----------------------------
    # Primary Identification
    # ----------------------------
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    # ----------------------------
    # Employee Details
    # ----------------------------
    em_id = models.CharField(max_length=64, unique=True, blank=True, null=True)
    em_role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="EMPLOYEE")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="ACTIVE")
    em_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    em_blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)

    designation = models.ForeignKey(
        "designation.Designation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees"
    )

    em_phone = models.CharField(max_length=64, blank=True, null=True)
    em_birthday = models.DateField(blank=True, null=True)
    em_joining_date = models.DateField(blank=True, null=True)
    em_contract_end = models.DateField(blank=True, null=True)
    em_image = models.ImageField(upload_to="images/employee/profile/", blank=True, null=True)
    em_nid = models.CharField(max_length=64, blank=True, null=True)

    # ----------------------------
    # Verification & OTP
    # ----------------------------
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_reset_otp = models.BooleanField(default=False)

    # ----------------------------
    # Password Reset
    # ----------------------------
    reset_password_token = models.UUIDField(blank=True, null=True)
    reset_password_token_created_at = models.DateTimeField(blank=True, null=True)

    # ----------------------------
    # Permissions & Auth
    # ----------------------------
    is_active = models.BooleanField(default=True)  
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # ----------------------------
    # Managers
    # ----------------------------
    objects = UserManager()
    active_objects = ActiveUserManager()

    # ----------------------------
    # Save override
    # ----------------------------
    def save(self, *args, **kwargs):
        if not self.em_id:
            self.em_id = f"EMP-{get_random_string(8).upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    @property
    def department(self):
        """Get department via designation (if assigned)."""
        return self.designation.department if self.designation else None

    # ----------------------------
    # OTP Methods
    # ----------------------------
    def set_otp(self, otp, reset=False):
        """Assign OTP to user (reset=True for password reset OTPs)."""
        self.otp = otp
        self.is_reset_otp = reset
        self.otp_created_at = timezone.now()
        self.save(update_fields=["otp", "otp_created_at", "is_reset_otp"])

    def verify_otp(self, otp, reset=False, expiry_minutes=10):
        """Verify OTP (valid for 10 minutes by default)."""
        if self.otp != otp or self.is_reset_otp != reset:
            return False
        if self.otp_created_at and timezone.now() > self.otp_created_at + timedelta(minutes=expiry_minutes):
            return False
        # Clear OTP after successful verification
        self.clear_otp()
        return True

    def clear_otp(self):
        """Clear OTP after use or expiry."""
        self.otp = None
        self.otp_created_at = None
        self.is_reset_otp = False
        self.save(update_fields=["otp", "otp_created_at", "is_reset_otp"])

    # ----------------------------
    # Password Reset Token Methods
    # ----------------------------
    def set_reset_password_token(self):
        """Generate a password reset token with timestamp."""
        self.reset_password_token = uuid.uuid4()
        self.reset_password_token_created_at = timezone.now()
        self.save(update_fields=["reset_password_token", "reset_password_token_created_at"])
        return self.reset_password_token

    def verify_reset_password_token(self, token, expiry_minutes=30):
        """Verify if reset token is valid (default expiry: 30 minutes)."""
        if str(self.reset_password_token) != str(token):
            return False
        if (
            self.reset_password_token_created_at
            and timezone.now() > self.reset_password_token_created_at + timedelta(minutes=expiry_minutes)
        ):
            return False
        return True

    def clear_reset_password_token(self):
        """Clear reset token after use or expiry."""
        self.reset_password_token = None
        self.reset_password_token_created_at = None
        self.save(update_fields=["reset_password_token", "reset_password_token_created_at"])
