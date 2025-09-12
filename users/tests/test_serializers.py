import uuid
from django.test import TestCase
from users.models import User
from rest_framework.test import APIRequestFactory
from rest_framework import serializers
from unittest.mock import patch
from users.serializers import (
    RegisterSerializer, 
    VerifyOTPSerializer, 
    ResendOTPSerializer, 
    ChangePasswordSerializer,
    MyTokenObtainPairSerializer,
    ForgotPasswordOTPSerializer,
    ResetPasswordOTPSerializer
)
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework.serializers import ValidationError

factory = APIRequestFactory()

class RegisterSerializerTests(TestCase):
    def setUp(self):
        self.valid_data = {
            "email": "test@gmail.com",
            "password": "test@123",
            "password_confirm": "test@123",
            "em_role": "EMPLOYEE",
            "em_phone": "+1234567890",
            "em_gender": "FEMALE"
        }

    def test_valid_registration(self):
        """Test successful user registration"""
        with patch('users.serializers.send_otp_email') as mock_send:
            serializer = RegisterSerializer(data=self.valid_data)
            self.assertTrue(serializer.is_valid())
            user = serializer.save()
            self.assertEqual(user.email, "test@gmail.com")
            self.assertFalse(user.is_verified)
            mock_send.assert_called_once()  

    def test_password_mismatch(self):
        """Test password confirmation mismatch"""
        data = self.valid_data.copy()
        data['password_confirm'] = "DifferentPass123!"
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password_confirm", serializer.errors)

    def test_duplicate_email(self):
        """Test registration with existing email"""
        User.objects.create_user(
            email="test@gmail.com",
            password="testpass123",
            em_role="EMPLOYEE"
        )
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_weak_password(self):
        """Test password validation"""
        data = self.valid_data.copy()
        data["password"] = data["password_confirm"] = "weak"
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_email_sending_failure(self):
        """Test rollback when OTP email fails"""
        with patch('users.serializers.send_otp_email', side_effect=Exception("SMTP error")):
            serializer = RegisterSerializer(data=self.valid_data)
            self.assertTrue(serializer.is_valid())
            with self.assertRaises(serializers.ValidationError):
                serializer.save()
            
            self.assertFalse(User.objects.filter(email=self.valid_data["email"]).exists())
    
class VerifyOTPSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@gmail.com",
            password="testpass123",
            em_role="EMPLOYEE",
            is_verified=False
        )
        self.user.set_otp("123456")

    def test_valid_otp_verification(self):
        """Test successful OTP verification"""
        data = {"email": "test@gmail.com", "otp": "123456"}
        serializer = VerifyOTPSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.validated_data
        self.assertTrue(user.is_verified)

    def test_invalid_otp(self):
        """Test invalid OTP"""
        data = {"email": "test@gmail.com", "otp": "wrong"}
        serializer = VerifyOTPSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_expired_otp(self):
        """Test expired OTP"""
        with patch.object(User, 'verify_otp', return_value=False):
            data = {"email": "test@gmail.com", "otp": "123456"}
            serializer = VerifyOTPSerializer(data=data)
            self.assertFalse(serializer.is_valid())

    def test_nonexistent_user(self):
        """Test verification for non-existent user"""
        data = {"email": "nonexistent@gmail.com", "otp": "123456"}
        serializer = VerifyOTPSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_already_verified_user(self):
        self.user.is_verified = True
        self.user.save()
        data = {"email": self.user.email, "otp": "123456"}
        serializer = VerifyOTPSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "User already verified"
        )

class ResendOTPSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@gmail.com",
            password="test@123",
            em_role="EMPLOYEE",
            is_verified=False
        )
    
    def test_valid_resend_request(self):
        """Test successful OTP resend"""
        with patch('core.utils.send_otp_email') as mock_send:
            data = {"email": "test@gmail.com"}
            serializer = ResendOTPSerializer(data=data)
            self.assertTrue(serializer.is_valid())
            user = serializer.save()
            self.assertEqual(user.email, "test@gmail.com")
            
    def test_nonexistent_user(self):
        """Test resend for non-existent user"""
        data = {"email": "nonexistent@gmail.com"}
        serializer = ResendOTPSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        
    def test_already_verified_user(self):
        """Test resend for already verified user"""
        self.user.is_verified = True
        self.user.save()
        data = {"email": "test@gmail.com"}
        serializer = ResendOTPSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        
    def test_email_sending_failure(self):
        """Test OTP resend failure"""
        data = {"email": self.user.email}

        with patch('users.serializers.send_otp_email', side_effect=Exception("SMTP error")):
            serializer = ResendOTPSerializer(data=data)
            self.assertTrue(serializer.is_valid())
            with self.assertRaises(serializers.ValidationError) as context:
                serializer.save()
            self.assertIn("Failed to resend OTP", str(context.exception))

class ChangePasswordSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@gmail.com",
            password="oldpass123",
            em_role="EMPLOYEE"
        )
        self.request = factory.post('/')
        self.request.user = self.user
    
    def test_valid_password_change(self):
        """Test successful password change"""
        data = {
            "old_password": "oldpass123",
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "NewSecurePass123!"
        }
        serializer = ChangePasswordSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertTrue(user.check_password("NewSecurePass123!"))

    def test_wrong_old_password(self):
        """Test with incorrect old password"""
        data = {
            "old_password": "wrongpass",
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "NewSecurePass123!"
        }
        serializer = ChangePasswordSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("old_password", serializer.errors)

    def test_password_mismatch(self):
        """Test new password confirmation mismatch"""
        data = {
            "old_password": "oldpass123",
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "DifferentPass123!"
        }
        serializer = ChangePasswordSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password_confirm", serializer.errors)
    
    def test_weak_new_password(self):
        """Test weak new password validation"""
        data = {
            "old_password": "oldpass123",
            "new_password": "weak",
            "new_password_confirm": "weak"
        }
        serializer = ChangePasswordSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password", serializer.errors)
    
class MyTokenObtainPairSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@gmail.com",
            password="testpass123",
            em_role="EMPLOYEE",
            is_verified=True
        )
    
    def test_valid_token_obtainment(self):
        """Test successful token generation"""
        data = {"email": "test@gmail.com", "password": "testpass123"}
        serializer = MyTokenObtainPairSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        token_data = serializer.validated_data
        self.assertIn("access", token_data)
        self.assertIn("refresh", token_data)
        self.assertEqual(token_data["email"], "test@gmail.com")
    
    def test_unverified_user(self):
        """Test token generation for unverified user"""
        self.user.is_verified = False
        self.user.save()
        data = {"email": "test@gmail.com", "password": "testpass123"}
        serializer = MyTokenObtainPairSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_token_payload(self):
        """Test token payload contains custom claims"""
        from rest_framework_simplejwt.tokens import RefreshToken
        
        token = MyTokenObtainPairSerializer.get_token(self.user)
        self.assertEqual(token["email"], "test@gmail.com")
        self.assertEqual(token["role"], "EMPLOYEE")
        self.assertEqual(token["user_id"], str(self.user.id))

class ForgotPasswordOTPSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@gmail.com",
            password="testpass123",
            em_role="EMPLOYEE"
        )

    def test_valid_forgot_password_request(self):
        """Test successful forgot password request"""
        with patch('core.utils.send_otp_email') as mock_send:
            data = {"email": "test@gmail.com"}
            serializer = ForgotPasswordOTPSerializer(data=data)
            self.assertTrue(serializer.is_valid())
            result = serializer.save()
            self.assertEqual(result["email"], "test@gmail.com")
            self.assertIsNotNone(result["token"])
    
    def test_nonexistent_user(self):
        """Test forgot password for non-existent user"""
        data = {"email": "nonexistent@gmail.com"}
        serializer = ForgotPasswordOTPSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_email_sending_failure(self):
        """Test forgot password email failure"""
        data = {"email": self.user.email}

        with patch('users.serializers.send_otp_email', side_effect=Exception("SMTP error")):
            serializer = ForgotPasswordOTPSerializer(data=data)
            self.assertTrue(serializer.is_valid())
            with self.assertRaises(ValidationError):
                serializer.save()

class ResetPasswordOTPSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@gmail.com",
            password="oldpass123",
            em_role="EMPLOYEE"
        )
        self.otp = "123456"
        self.user.set_otp(self.otp, reset=True)
        self.reset_token = self.user.set_reset_password_token()

    def test_valid_password_reset(self):
        """Test successful password reset"""
        data = {
            "email": self.user.email,
            "otp": self.otp,
            "token": self.reset_token,
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "NewSecurePass123!"
        }

        serializer = ResetPasswordOTPSerializer(data=data)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        user = serializer.save()
        self.assertTrue(user.check_password("NewSecurePass123!"))

    def test_invalid_otp(self):
        """Test reset with invalid OTP"""
        data = {
            "email": self.user.email,
            "otp": "wrong",
            "token": self.reset_token,
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "NewSecurePass123!"
        }
        serializer = ResetPasswordOTPSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Invalid or expired OTP", str(serializer.errors))

    def test_invalid_token(self):
        """Test reset with invalid token"""
        data = {
            "email": self.user.email,
            "otp": self.otp,
            "token": uuid.uuid4(),  
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "NewSecurePass123!"
        }
        serializer = ResetPasswordOTPSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Invalid or expired reset token", str(serializer.errors))

    def test_password_mismatch(self):
        """Test reset with password mismatch"""
        data = {
            "email": self.user.email,
            "otp": self.otp,
            "token": self.reset_token,
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "DifferentPass123!"
        }
        serializer = ResetPasswordOTPSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Passwords do not match", str(serializer.errors))

    def test_nonexistent_user(self):
        """Test reset for non-existent user"""
        data = {
            "email": "nonexistent@gmail.com",
            "otp": self.otp,
            "token": self.reset_token,
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "NewSecurePass123!"
        }
        serializer = ResetPasswordOTPSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Invalid email", str(serializer.errors))