from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from unittest.mock import patch
from users.models import User
from django.test import override_settings
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken

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
    
    def test_resend_email_failure(self):
        """Test OTP resend when email fails"""
        with patch('users.serializers.send_otp_email', side_effect=Exception("SMTP error")):
            data = {"email": "test@gmail.com"}
            response = self.client.post(self.resend_otp_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class LoginViewTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.login_url = reverse("accounts:login")

        self.user = User.objects.create_user(
            email="test@gmail.com",
            password="StrongPass123",
            em_role="EMPLOYEE",
            em_phone="1234567890",
            em_gender="MALE",
        )
        self.user.is_verified = True  
        self.user.save()

    @override_settings(REST_FRAMEWORK={"DEFAULT_THROTTLE_RATES": {"login": "1000/hour"}})
    def test_successful_login(self):
        """Test successful login"""
        data = {"email": "test@gmail.com", "password": "StrongPass123"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_unverified_user(self):
        """Test login for unverified user"""
        self.user.is_verified = False
        self.user.save()
        data = {"email":"test@gmail.com", "password":"StrongPass123"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {"email":"test@gmail.com", "password":"wrongPassword"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_throttling(self):
        """Ensure login is throttled after too many attempts"""
        data = {
        "email": "test@gmail.com",
        "password": "StrongPass123"
        }
        for i in range(40): 
            response = self.client.post(self.login_url, data, format="json")
            last_status = response.status_code
        self.assertEqual(last_status, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"].code, "throttled")

class LogoutViewTests(APITestCase):
    def setUp(self):
        self.logout_url = reverse("accounts:logout")

        self.user = User.objects.create_user(
            email="test@gmail.com",
            password="StrongPass123",
            em_role="EMPLOYEE",
            em_phone="1234567890",
            em_gender="MALE",
            is_verified=True
        )

        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_successful_logout(self):
        """Test successful logout"""
        refresh = RefreshToken.for_user(self.user)
        data = {"refresh": str(refresh)}
        response = self.client.post(self.logout_url, data)
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
    
    def test_logout_without_refresh_token(self):
        """Test logout without refresh token"""
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_with_invalid_token(self):
        """Test logout with invalid token"""
        data = {"refresh": "invalid_token"}
        response = self.client.post(self.logout_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_logout_unauthenticated(self):
        """Test logout without authentication"""
        client = APIClient()
        response = client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class ChangePasswordViewTests(APITestCase):
    def setUp(self):
        self.change_password_url = reverse("accounts:change-password")

        self.user = User.objects.create_user(
            email="test@gmail.com",
            password="StrongPass123",
            em_role="EMPLOYEE",
            em_phone="1234567890",
            em_gender="MALE",
            is_verified=True
        )

        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_successful_password_change(self):
        """Test successful password change"""
        data = {
                "old_password": "StrongPass123",  
                "new_password": "NewSecurePass123!",
                "new_password_confirm": "NewSecurePass123!"
        }
        response = self.client.put(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewSecurePass123!"))
    
    def test_password_change_wrong_old_password(self):
        """Test password change with wrong old password"""
        data = {
            "old_password": "wrongpass",
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "NewSecurePass123!"
        }
        response = self.client.put(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_change_password_mismatch(self):
        """Test password change with password mismatch"""
        data = {
            "old_password": "StrongPass123",
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "DifferentPass123!"
        }
        response = self.client.put(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_change_unauthenticated(self):
        """Test password change without authentication"""
        client = APIClient() 
        response = client.put(self.change_password_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
class ForgotPasswordViewTests(APITestCase):
    def setUp(self):
        self.forgot_password_url = reverse("accounts:forgot-password")

        self.user = User.objects.create_user(
            email="test@gmail.com",
            password="StrongPass123",
            em_role="EMPLOYEE",
            em_phone="1234567890",
            em_gender="MALE",
            is_verified=True
        )

    def test_successful_forgot_password_request(self):
        """Test successful forgot password request"""
        with patch('users.serializers.send_otp_email') as mock_send:
            data = {"email": "test@gmail.com"}
            response = self.client.post(self.forgot_password_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("email", response.data["data"])
            self.assertIn("token", response.data["data"])
    
    def test_forgot_password_nonexistent_user(self):
        """Test forgot password for non-existent user"""
        data = {"email": "nonexistent@gmail.com"}
        response = self.client.post(self.forgot_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_forgot_password_email_failure(self):
        """Test forgot password when email fails"""
        with patch('users.serializers.send_otp_email', side_effect=Exception("SMTP error")):
            data = {"email": "test@gmail.com"}
            response = self.client.post(self.forgot_password_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class ResetPasswordViewTests(APITestCase):
    def setUp(self):
        self.reset_password_url = reverse("accounts:reset-password")

        self.user = User.objects.create_user(
            email="test@gmail.com",
            password="StrongPass123",
            em_role="EMPLOYEE",
            em_phone="1234567890",
            em_gender="MALE",
            is_verified=True
        )
        
        self.reset_token = self.user.set_reset_password_token()
        self.user.set_otp("123456", reset=True)

    def test_successful_password_reset(self):
        """Test successful password reset"""
        data = {
            "email": "test@gmail.com",
            "otp": "123456",
            "token": self.reset_token,
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "NewSecurePass123!"
        }
        response = self.client.post(self.reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewSecurePass123!"))
        self.assertIsNone(self.user.reset_password_token)
    
    def test_password_reset_invalid_otp(self):
        """Test password reset with invalid OTP"""
        data = {
            "email": "test@gmail.com",
            "otp": "wrong",
            "token": self.reset_token,
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "NewSecurePass123!"
        }
        response = self.client.post(self.reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_reset_invalid_token(self):
        """Test password reset with invalid token"""
        data = {
            "email": "test@gmail.com",
            "otp": "123456",
            "token": "invalid-uuid-token",
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "NewSecurePass123!"
        }
        response = self.client.post(self.reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_password_mismatch(self):
        """Test password reset with password mismatch"""
        data = {
            "email": "test@gmail.com",
            "otp": "123456",
            "token": self.reset_token,
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "DifferentPass123!"
        }
        response = self.client.post(self.reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        