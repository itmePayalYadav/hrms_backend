import uuid
from django.db import models
from core.models import BaseModel
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _
from .managers import UserManager, ActiveUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from core.constants import (
    ROLE_CHOICES, 
    STATUS_CHOICES, 
    GENDER_CHOICES, 
    BLOOD_GROUP_CHOICES,
    ADDRESS_TYPE_CHOICES
)

# ----------------------------
# User Model
# ----------------------------
class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), unique=True)
    
    em_id = models.CharField(max_length=64, unique=True, blank=True, null=True)
    em_role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="EMPLOYEE")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="ACTIVE")
    em_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="MALE")
    em_blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, default="O+")
    des_id = models.ForeignKey('Designation', on_delete=models.SET_NULL, null=True, blank=True)
    dep_id = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    em_phone = models.CharField(max_length=64, blank=True, null=True)
    em_birthday = models.DateField(blank=True, null=True)
    em_joining_date = models.DateField(blank=True, null=True)
    em_contract_end = models.DateField(blank=True, null=True)
    em_image = models.ImageField(upload_to="images/employee/profile/", blank=True, null=True)
    em_nid = models.CharField(max_length=64, blank=True, null=True)
    
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
    active_objects = ActiveUserManager()

    def __str__(self):
        return self.email
    
    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

# ----------------------------
# Department & Designation
# ----------------------------
class Department(models.Model):
    dep_name = models.CharField(max_length=64)

    def __str__(self):
        return self.dep_name


class Designation(models.Model):
    des_name = models.CharField(max_length=64)

    def __str__(self):
        return self.des_name
