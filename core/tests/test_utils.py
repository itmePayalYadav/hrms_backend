import unittest
from unittest.mock import patch
from smtplib import SMTPException
from rest_framework import status
from rest_framework.response import Response

from core.utils import generate_otp, _send_otp_email_sync, send_otp_email, api_response

class UtilsTests(unittest.TestCase):
    # ----------------------------
    # Test OTP generator
    # ----------------------------
    def test_generate_otp_length(self):
        otp = generate_otp(6)
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())
    
    def test_generate_otp_custom_length(self):
        otp = generate_otp(8)
        self.assertEqual(len(otp), 8)
        self.assertTrue(otp.isdigit())
    
    def test_generate_otp_invalid_length(self):
        with self.assertRaises(ValueError):
            generate_otp(0)
    
    # ----------------------------
    # Test asynchronous OTP email sender
    # ----------------------------

    @patch("core.utils._send_otp_email_sync")
    def test_send_otp_email_async_calls_sync(self, mock_sync):
        send_otp_email("test@gmail.com", "123456")
        import time
        time.sleep(0.1)
        mock_sync.assert_called_once_with("test@gmail.com", "123456", 10) 

        # ----------------------------
    # Test API response utility
    # ----------------------------
    def test_api_response_default(self):
        resp = api_response(message="Success")
        self.assertIsInstance(resp, Response)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["status"], "success")
        self.assertEqual(resp.data["message"], "Success")

    def test_api_response_with_data_and_errors(self):
        resp = api_response(
            status_str="error",
            message="Failed",
            data={"foo": "bar"},
            errors={"field": "error"},
            status_code=status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["status"], "error")
        self.assertEqual(resp.data["data"]["foo"], "bar")
        self.assertEqual(resp.data["errors"]["field"], "error")
        