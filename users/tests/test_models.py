from django.test import TestCase
from users.models import User, Department, Designation

class TestUserModel(TestCase):
    def setUp(self):
        self.department = Department.objects.create(dep_name="IT")
        self.designation = Designation.objects.create(des_name="Development")

    def test_create_user(self):  
        user = User.objects.create_user(
            email="test@gmail.com",
            password="test@123",
            em_role="EMPLOYEE",
            dep_id=self.department,
            des_id=self.designation,
            em_phone="1234567890"
        )

        self.assertEqual(user.email, "test@gmail.com")
        self.assertTrue(user.check_password("test@123"))
        self.assertEqual(user.em_role, "EMPLOYEE")
        self.assertEqual(user.dep_id, self.department)
        self.assertEqual(user.des_id, self.designation)
        self.assertEqual(user.em_phone, "1234567890")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_verified)

    def test_create_admin(self):  
        user = User.objects.create_admin(
            email="admin@gmail.com",
            password="admin@123",
            em_role="ADMIN",
        )
        
        self.assertEqual(user.email, "admin@gmail.com")
        self.assertTrue(user.check_password("admin@123"))
        self.assertEqual(user.em_role, "ADMIN")
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_verified)
    
    def test_create_superuser(self):  
        user = User.objects.create_superuser(
            email="superadmin@gmail.com",
            password="superadmin@123",
            em_role="SUPER_ADMIN",
        )
        
        self.assertEqual(user.email, "superadmin@gmail.com")
        self.assertTrue(user.check_password("superadmin@123"))
        self.assertEqual(user.em_role, "SUPER_ADMIN")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertFalse(user.is_verified)
    
    def test_create_user_no_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password="test@123")
    
    def test_soft_delete_and_restore(self):
        user = User.objects.create_user(email="testdelete@gmail.com", password="test@123")
        
        user.delete()
        self.assertTrue(user.is_deleted)
        self.assertFalse(User.active_objects.filter(email="testdelete@gmail.com").exists())
        
        user.restore()
        self.assertFalse(user.is_deleted)
        self.assertTrue(User.active_objects.filter(email="testdelete@gmail.com").exists())
    
    def test_otp_storage(self):
        user = User.objects.create_user(email="otp@gmail.com", password="otp@123")
        user.otp = "123456"
        user.save()
        res = User.objects.get(email="otp@gmail.com")
        self.assertTrue(res.otp, "123456")
    
    def test_user_string_representation(self):
        user = User.objects.create_user(email="test@gmail.com", password="test@123")
        self.assertEqual(str(user), "test@gmail.com")
    
    def test_user_default_values(self):
        user = User.objects.create_user(email="default@gmail.com", password="default@123")
        self.assertFalse(user.is_verified)
        self.assertIsNone(user.otp)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_superuser_validation(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="superadmin@gmail.com",
                password="supeeradmin@123",
                is_staff=False
            )
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="superadmin@gmail.com",
                password="supeeradmin@123",
                is_superuser=False
            )
    
    def test_email_normalization(self):
        user = User.objects.create_user(email="TEST@GMAIL.COM", password="test@123")
        self.assertEqual(user.email, "TEST@gmail.com") 
            
class DepartmentDesignationTests(TestCase):
    def test_department_creation(self):
        department = Department.objects.create(dep_name="HR")
        self.assertEqual(str(department), "HR")

    def test_designation_creation(self):
        designation = Designation.objects.create(des_name="Manager")
        self.assertEqual(str(designation), "Manager")
    