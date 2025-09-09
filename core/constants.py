from django.utils.translation import gettext_lazy as _

# ----------------------------
# User Roles
# ----------------------------
ROLE_CHOICES = (
    ("SUPER_ADMIN", _("Super Admin")),
    ("ADMIN", _("Admin")),
    ("EMPLOYEE", _("Employee")),
)

# ----------------------------
# General Status
# ----------------------------
STATUS_CHOICES = (
    ("ACTIVE", _("Active")),
    ("INACTIVE", _("Inactive")),
)

# ----------------------------
# Gender
# ----------------------------
GENDER_CHOICES = (
    ("MALE", _("Male")),
    ("FEMALE", _("Female")),
    ("OTHER", _("Other")),
)

# ----------------------------
# Blood Groups
# ----------------------------
BLOOD_GROUP_CHOICES = (
    ("O_POS", _("O+")),
    ("O_NEG", _("O-")),
    ("A_POS", _("A+")),
    ("A_NEG", _("A-")),
    ("B_POS", _("B+")),
    ("B_NEG", _("B-")),
    ("AB_POS", _("AB+")),
    ("AB_NEG", _("AB-")),
)

# ----------------------------
# Leave Status
# ----------------------------
LEAVE_STATUS_CHOICES = (
    ("PENDING", _("Pending")),
    ("APPROVED", _("Approved")),
    ("REJECTED", _("Rejected")),
    ("NOT_APPROVED", _("Not Approved")),
)

# ----------------------------
# Address Type
# ----------------------------
ADDRESS_TYPE_CHOICES = (
    ("PRESENT", _("Present")),
    ("TEMPORARY", _("Temporary")),
    ("PERMANENT", _("Permanent")),
)

# ----------------------------
# Education Levels
# ----------------------------
EDUCATION_LEVEL_CHOICES = (
    ("HIGH_SCHOOL", _("High School")),
    ("DIPLOMA", _("Diploma")),
    ("BACHELOR", _("Bachelor")),
    ("MASTER", _("Master")),
    ("PHD", _("PhD")),
)

# ----------------------------
# Field Visit Status
# ----------------------------
FIELD_VISIT_STATUS_CHOICES = (
    ("PENDING", _("Pending Approval")),
    ("APPROVED", _("Approved")),
    ("REJECTED", _("Rejected")),
    ("IN_PROGRESS", _("In Progress")),
    ("COMPLETED", _("Completed")),
    ("CANCELLED", _("Cancelled")),
)

# ----------------------------
# Resource Status
# ----------------------------
RESOURCE_STATUS_CHOICES = (
    ("AVAILABLE", _("Available")),
    ("USED", _("Used")),
    ("EXPIRED", _("Expired")),
)

# ----------------------------
# Severity Levels
# ----------------------------
SEVERITY_CHOICES = (
    ("MINOR", _("Minor")),
    ("MODERATE", _("Moderate")),
    ("SEVERE", _("Severe")),
)

# ----------------------------
# Penalty Status
# ----------------------------
PENALTY_STATUS_CHOICES = (
    ("PENDING", _("Pending")),
    ("RESOLVED", _("Resolved")),
    ("DISMISSED", _("Dismissed")),
)

# ----------------------------
# Inventory Status
# ----------------------------
INVENTORY_STATUS_CHOICES = (
    ("ASSETS", _("Assets")),
    ("LOGISTICS", _("Logistics")),
)

# ----------------------------
# Project Status Choices
# ----------------------------
PROJECT_STATUS_CHOICES = [
    ('planned', _('Planned')),
    ('running', _('Running')),
    ('completed', _('Completed')),
    ('on_hold', _('On Hold')),
    ('cancelled', _('Cancelled')),
]

# ----------------------------
# Task Type Choices
# ----------------------------
TASK_TYPE_CHOICES = [
    ('office', _('Office')),
    ('field', _('Field')),
    ('remote', _('Remote')),
    ('other', _('Other')),
]

# ----------------------------
# Task Status Choices
# ----------------------------
TASK_STATUS_CHOICES = [
    ('not_started', _('Not Started')),
    ('in_progress', _('In Progress')),
    ('completed', _('Completed')),
    ('blocked', _('Blocked')),
    ('on_hold', _('On Hold')),
]

# ----------------------------
# Loan Status
# ----------------------------
LOAN_STATUS_CHOICES = [
    ('Pause', 'Pause'),
    ('Active', 'Active'),
    ('Closed', 'Closed'),
]

# ----------------------------
# Payment Status Choices
# ----------------------------
PAYMENT_STATUS_CHOICES = (
    ("PROCESS", _("Process")),
    ("PAID", _("Paid")),
    ("FAILED", _("Failed")),
    ("PENDING", _("Pending")),
)

# ----------------------------
# Payment Type Choices
# ----------------------------
PAYMENT_TYPE_CHOICES = (
    ("BANK", _("Bank Transfer")),
    ("CASH", _("Cash")),
    ("CHECK", _("Check")),
    ("OTHER", _("Other")),
)

# ----------------------------
# User Type Choices
# ----------------------------
USER_TYPE_CHOICES = (
    ('Owner', 'Owner'),
    ('Manager', 'Manager'),
    ('Team Lead', 'Team Lead'),
    ('Developer', 'Developer'),
    ('Tester', 'Tester'),
    ('Collaborators', 'Collaborators'),  
)
