<!-- from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# Department Model
class Department(models.Model):
    name = models.CharField(max_length=64, unique=True)
    
    def __str__(self):
        return self.name

# Designation Model
class Designation(models.Model):
    name = models.CharField(max_length=64, unique=True)
    
    def __str__(self):
        return self.name

# Employee Model (Custom User)
class Employee(AbstractBaseUser):
    ROLE_CHOICES = (
        ('ADMIN', 'ADMIN'),
        ('EMPLOYEE', 'EMPLOYEE'),
        ('SUPER ADMIN', 'SUPER ADMIN'),
    )
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    BLOOD_GROUP_CHOICES = (
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('OB+', 'OB+'),
    )
    STATUS_CHOICES = (
        ('ACTIVE', 'ACTIVE'),
        ('INACTIVE', 'INACTIVE'),
    )
    
    em_id = models.CharField(max_length=64, unique=True)
    em_code = models.CharField(max_length=64, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')
    address = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    phone = models.CharField(max_length=64, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    contact_end = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to='employee_images/', blank=True, null=True)
    nid = models.CharField(max_length=64, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = CustomUserManager()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.em_id})"

# Address Model
class Address(models.Model):
    TYPE_CHOICES = (
        ('Present', 'Present'),
        ('Permanent', 'Permanent'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='addresses')
    city = models.CharField(max_length=128, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='Present')
    
    def __str__(self):
        return f"{self.employee.em_id} - {self.type} Address"

# Education Model
class Education(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='educations')
    edu_type = models.CharField(max_length=256, blank=True, null=True)
    institute = models.CharField(max_length=256, blank=True, null=True)
    result = models.CharField(max_length=64, blank=True, null=True)
    year = models.CharField(max_length=64, blank=True, null=True)
    
    def __str__(self):
        return f"{self.employee.em_id} - {self.edu_type}"

# BankInfo Model
class BankInfo(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='bank_info')
    holder_name = models.CharField(max_length=256, blank=True, null=True)
    bank_name = models.CharField(max_length=256, blank=True, null=True)
    branch_name = models.CharField(max_length=256, blank=True, null=True)
    account_number = models.CharField(max_length=256, blank=True, null=True)
    account_type = models.CharField(max_length=256, blank=True, null=True)
    
    def __str__(self):
        return f"{self.employee.em_id} - {self.bank_name}"

# SocialMedia Model
class SocialMedia(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='social_media')
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    google_plus = models.URLField(blank=True, null=True)
    skype_id = models.CharField(max_length=256, blank=True, null=True)
    
    def __str__(self):
        return f"{self.employee.em_id} - Social Media"

# EmployeeFile Model
class EmployeeFile(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='files')
    file_title = models.CharField(max_length=512, blank=True, null=True)
    file_url = models.FileField(upload_to='employee_files/')
    
    def __str__(self):
        return f"{self.employee.em_id} - {self.file_title}"

# LeaveTypes Model
class LeaveType(models.Model):
    name = models.CharField(max_length=64)
    leave_day = models.CharField(max_length=255, blank=True, null=True)
    status = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

# AssignLeave Model
class AssignLeave(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assigned_leaves')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    day = models.CharField(max_length=256, blank=True, null=True)
    hour = models.CharField(max_length=255, default='0')
    total_day = models.CharField(max_length=64, blank=True, null=True)
    dateyear = models.CharField(max_length=64, blank=True, null=True)
    
    def __str__(self):
        return f"{self.employee.em_id} - {self.leave_type.name}"

# EmpLeave Model
class EmpLeave(models.Model):
    STATUS_CHOICES = (
        ('Approve', 'Approve'),
        ('Not Approve', 'Not Approve'),
        ('Rejected', 'Rejected'),
    )
    DURATION_CHOICES = (
        ('Full Day', 'Full Day'),
        ('Half Day', 'Half Day'),
        ('More than One day', 'More than One day'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    leave_duration = models.CharField(max_length=128, blank=True, null=True)
    apply_date = models.DateField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Approve')
    
    def __str__(self):
        return f"{self.employee.em_id} - {self.leave_type.name}"

# EarnedLeave Model
class EarnedLeave(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='earned_leaves')
    present_date = models.CharField(max_length=64, blank=True, null=True)
    hour = models.CharField(max_length=64, blank=True, null=True)
    status = models.CharField(max_length=64, blank=True, null=True)
    
    def __str__(self):
        return f"{self.employee.em_id} - Earned Leave"

# SalaryType Model
class SalaryType(models.Model):
    salary_type = models.CharField(max_length=256, blank=True, null=True)
    create_date = models.CharField(max_length=256, blank=True, null=True)
    
    def __str__(self):
        return self.salary_type

# EmpSalary Model
class EmpSalary(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='salary')
    salary_type = models.ForeignKey(SalaryType, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.employee.em_id} - Salary"

# Addition Model
class Addition(models.Model):
    salary = models.ForeignKey(EmpSalary, on_delete=models.CASCADE, related_name='additions')
    basic = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    medical = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    house_rent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    conveyance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"Addition for {self.salary.employee.em_id}"

# Deduction Model
class Deduction(models.Model):
    salary = models.ForeignKey(EmpSalary, on_delete=models.CASCADE, related_name='deductions')
    provident_fund = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bima = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    others = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"Deduction for {self.salary.employee.em_id}"

# PaySalary Model
class PaySalary(models.Model):
    STATUS_CHOICES = (
        ('Paid', 'Paid'),
        ('Process', 'Process'),
    )
    PAYMENT_CHOICES = (
        ('Hand Cash', 'Hand Cash'),
        ('Bank', 'Bank'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_payments')
    salary_type = models.ForeignKey(SalaryType, on_delete=models.CASCADE)
    month = models.CharField(max_length=64, blank=True, null=True)
    year = models.CharField(max_length=64, blank=True, null=True)
    paid_date = models.DateField(blank=True, null=True)
    total_days = models.CharField(max_length=64, blank=True, null=True)
    basic = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    medical = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    house_rent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bima = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    provident_fund = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    loan = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_pay = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    addition = models.IntegerField(default=0)
    deduction = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Process')
    paid_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='Bank')
    
    def __str__(self):
        return f"{self.employee.em_id} - {self.month}/{self.year}"

# Loan Model
class Loan(models.Model):
    STATUS_CHOICES = (
        ('Granted', 'Granted'),
        ('Deny', 'Deny'),
        ('Pause', 'Pause'),
        ('Done', 'Done'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_pay = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_due = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    installment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    loan_number = models.CharField(max_length=256, blank=True, null=True)
    loan_details = models.TextField(blank=True, null=True)
    approve_date = models.DateField(blank=True, null=True)
    install_period = models.CharField(max_length=256, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pause')
    
    def __str__(self):
        return f"{self.employee.em_id} - Loan #{self.loan_number}"

# LoanInstallment Model
class LoanInstallment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='installments')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    loan_number = models.CharField(max_length=256, blank=True, null=True)
    install_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pay_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    app_date = models.DateField(blank=True, null=True)
    receiver = models.CharField(max_length=256, blank=True, null=True)
    install_no = models.CharField(max_length=256, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Installment #{self.install_no} for Loan #{self.loan_number}"

# Attendance Model
class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    atten_date = models.DateField()
    signin_time = models.TimeField(blank=True, null=True)
    signout_time = models.TimeField(blank=True, null=True)
    working_hour = models.CharField(max_length=64, blank=True, null=True)
    place = models.CharField(max_length=255, default='office')
    absence = models.CharField(max_length=128, blank=True, null=True)
    overtime = models.CharField(max_length=128, blank=True, null=True)
    earnleave = models.CharField(max_length=128, blank=True, null=True)
    status = models.CharField(max_length=64, blank=True, null=True)
    
    def __str__(self):
        return f"{self.employee.em_id} - {self.atten_date}"

# Holiday Model
class Holiday(models.Model):
    holiday_name = models.CharField(max_length=256, blank=True, null=True)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    number_of_days = models.CharField(max_length=64, blank=True, null=True)
    year = models.CharField(max_length=64, blank=True, null=True)
    
    def __str__(self):
        return self.holiday_name

# AssetsCategory Model
class AssetsCategory(models.Model):
    CATEGORY_CHOICES = (
        ('ASSETS', 'ASSETS'),
        ('LOGISTIC', 'LOGISTIC'),
    )
    
    name = models.CharField(max_length=256)
    category_type = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='ASSETS')
    
    def __str__(self):
        return f"{self.name} ({self.category_type})"

# Assets Model
class Asset(models.Model):
    category = models.ForeignKey(AssetsCategory, on_delete=models.CASCADE, related_name='assets')
    name = models.CharField(max_length=256, blank=True, null=True)
    brand = models.CharField(max_length=128, blank=True, null=True)
    model = models.CharField(max_length=256, blank=True, null=True)
    code = models.CharField(max_length=256, blank=True, null=True)
    configuration = models.TextField(blank=True, null=True)
    purchasing_date = models.DateField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity = models.IntegerField(default=0)
    in_stock = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} - {self.brand}"

# EmpAssets Model
class EmpAsset(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assets')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    given_date = models.DateField()
    return_date = models.DateField()
    
    def __str__(self):
        return f"{self.employee.em_id} - {self.asset.name}"

# LogisticAsset Model
class LogisticAsset(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    quantity = models.IntegerField(default=0)
    entry_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.name

# Project Model
class Project(models.Model):
    STATUS_CHOICES = (
        ('upcoming', 'upcoming'),
        ('complete', 'complete'),
        ('running', 'running'),
    )
    
    name = models.CharField(max_length=128)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    summary = models.CharField(max_length=512, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='running')
    progress = models.CharField(max_length=128, blank=True, null=True)
    
    def __str__(self):
        return self.name

# ProjectTask Model
class ProjectTask(models.Model):
    TASK_TYPE_CHOICES = (
        ('Office', 'Office'),
        ('Field', 'Field'),
    )
    STATUS_CHOICES = (
        ('running', 'running'),
        ('complete', 'complete'),
        ('cancel', 'cancel'),
    )
    APPROVAL_CHOICES = (
        ('Approved', 'Approved'),
        ('Not Approve', 'Not Approve'),
        ('Rejected', 'Rejected'),
    )
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=256)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to='task_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    task_type = models.CharField(max_length=10, choices=TASK_TYPE_CHOICES, default='Office')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='running')
    location = models.CharField(max_length=512, blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    total_days = models.CharField(max_length=128, blank=True, null=True)
    create_date = models.DateField(blank=True, null=True)
    approve_status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='Not Approve')
    
    def __str__(self):
        return f"{self.project.name} - {self.title}"

# AssignTask Model
class AssignTask(models.Model):
    USER_TYPE_CHOICES = (
        ('Team Head', 'Team Head'),
        ('Collaborators', 'Collaborators'),
    )
    
    task = models.ForeignKey(ProjectTask, on_delete=models.CASCADE, related_name='assignments')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='Collaborators')
    
    def __str__(self):
        return f"{self.employee.em_id} - {self.task.title}"

# ProjectFile Model
class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    details = models.TextField(blank=True, null=True)
    file_url = models.FileField(upload_to='project_files/')
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.project.name} - File"

# ProjectExpenses Model
class ProjectExpense(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='expenses')
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.project.name} - Expense"

# ProjectNotes Model
class ProjectNote(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='notes')
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.project.name} - Note"

# FieldVisit Model
class FieldVisit(models.Model):
    STATUS_CHOICES = (
        ('Approved', 'Approved'),
        ('Not Approve', 'Not Approve'),
        ('Rejected', 'Rejected'),
    )
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='field_visits')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    location = models.CharField(max_length=512)
    start_date = models.DateField(blank=True, null=True)
    approx_end_date = models.DateField()
    total_days = models.CharField(max_length=64, blank=True, null=True)
    notes = models.TextField()
    actual_return_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Approve')
    attendance_updated = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.employee.em_id} - {self.project.name}"

# Desciplinary Model
class Desciplinary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='desciplinary_actions')
    action = models.CharField(max_length=256, blank=True, null=True)
    title = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.employee.em_id} - {self.title}"

# Notice Model
class Notice(models.Model):
    title = models.TextField()
    file_url = models.FileField(upload_to='notices/', blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.title

# ToDoList Model
class ToDoList(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='todo_items')
    task = models.CharField(max_length=256)
    date = models.DateTimeField()
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.employee.em_id} - {self.task}"

# Settings Model
class Settings(models.Model):
    sitelogo = models.ImageField(upload_to='settings/', blank=True, null=True)
    sitetitle = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    copyright = models.CharField(max_length=128, blank=True, null=True)
    contact = models.CharField(max_length=128, blank=True, null=True)
    currency = models.CharField(max_length=128, blank=True, null=True)
    symbol = models.CharField(max_length=64, blank=True, null=True)
    system_email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=256, blank=True, null=True)
    address2 = models.CharField(max_length=256, blank=True, null=True)
    
    def __str__(self):
        return "System Settings" -->