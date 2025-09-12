from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from unittest.mock import patch
from users.models import User
from django.test import override_settings

class RegisterViewTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("accounts:register")

        self.valid_data = {
            "email": "test@gmail.com",
            "password": "StrongPass123",
            "password_confirm": "StrongPass123",
            "em_role": "EMPLOYEE",
            "em_phone": "1234567890",
            "em_gender": "MALE"
        }

    def test_successful_registration(self):
        """Test successful user registration"""
        with patch("users.serializers.send_otp_email") as mock_send:
            response = self.client.post(self.register_url, self.valid_data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(User.objects.count(), 1)
            self.assertEqual(User.objects.get().email, "test@gmail.com")
            mock_send.assert_called_once() 

    def test_registration_with_existing_email(self):
        """Test registration with existing email fails"""
        User.objects.create_user(
            email="test@gmail.com",
            password="testpass123",
            em_role="EMPLOYEE"
        )
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1) 
        
    def test_registration_password_mismatch(self):
        """Test registration with password mismatch"""
        data = self.valid_data.copy()
        data["password_confirm"] = "DifferentPass123!"
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_email_sending_failure(self):
        """Test registration when OTP email fails"""
        with patch('users.serializers.send_otp_email', side_effect=Exception("SMTP error")):
            response = self.client.post(self.register_url, self.valid_data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(User.objects.count(), 0)

class VerifyOTPViewTests(APITestCase):
    def setUp(self):
        self.verify_otp_url = reverse("accounts:verify-otp")

        self.valid_data = {
            "email": "test@gmail.com",
            "password": "StrongPass123",
            "password_confirm": "StrongPass123",
            "em_role": "EMPLOYEE",
            "em_phone": "1234567890",
            "em_gender": "MALE",
            "is_verified": False,
        }

        self.user = User.objects.create_user(
            email=self.valid_data["email"],
            password=self.valid_data["password"],
            em_role=self.valid_data["em_role"],
            em_phone=self.valid_data["em_phone"],
            em_gender=self.valid_data["em_gender"],
            is_verified=self.valid_data["is_verified"],
        )

        self.user.set_otp("123456")
        self.user.save()
    
    def test_successful_otp_verification(self):
        """Test successful OTP verification"""
        data = {"email": "test@gmail.com", "otp": "123456"}
        response = self.client.post(self.verify_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)
        
    def test_invalid_otp(self):
        """Test verification with invalid OTP"""
        data = {"email": "test@gmail.com", "otp": "wrong"}
        response = self.client.post(self.verify_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_nonexistent_user_verification(self):
        """Test verification for non-existent user"""
        data = {"email": "nonexistent@example.com", "otp": "123456"}
        response = self.client.post(self.verify_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class ResendOTPViewTests(APITestCase):
    def setUp(self):
        self.resend_otp_url = reverse("accounts:resend-otp")
        
        self.valid_data = {
                "email": "test@gmail.com",
                "password": "StrongPass123",
                "password_confirm": "StrongPass123",
                "em_role": "EMPLOYEE",
                "em_phone": "1234567890",
                "em_gender": "MALE",
                "is_verified": False,
            }
        
        self.user = User.objects.create_user(
            email=self.valid_data["email"],
            password=self.valid_data["password"],
            em_role=self.valid_data["em_role"],
            em_phone=self.valid_data["em_phone"],
            em_gender=self.valid_data["em_gender"],
            is_verified=self.valid_data["is_verified"],
        )
        self.user.set_otp("123456")
        self.user.save()
    
    def test_successful_otp_resend(self):
        """Test successful OTP resend"""
        with patch('users.serializers.send_otp_email') as mock_send:
            data = {"email": "test@gmail.com"}
            response = self.client.post(self.resend_otp_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_resend_for_verified_user(self):
        """Test OTP resend for already verified user"""
        self.user.is_verified = True
        self.user.save()
        data = {"email": "test@gmail.com"}
        response = self.client.post(self.resend_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_resend_for_nonexistent_user(self):
        """Test OTP resend for non-existent user"""
        data = {"email": "nonexistent@gmail.com"}
        response = self.client.post(self.resend_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
