from .models import User
from django.contrib import admin
from designation.models import Designation
from department.models import Department
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# ----------------------------
# Custom User Admin
# ----------------------------
class UserAdmin(BaseUserAdmin):
    """
    Custom configuration for User model in Django Admin.
    Includes:
    - Custom list display and filters
    - Grouped fieldsets for better UI
    - Custom add user form fields
    """

    # ----------------------------
    # List view settings
    # ----------------------------
    list_display = ("email", "em_role", "status", "is_staff", "is_superuser", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active", "em_role", "status")
    
    # ----------------------------
    # Fieldsets (edit view)
    # ----------------------------
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {
            "fields": (
                "em_id", "em_role", "status", "em_gender", "em_blood_group",
                "em_phone", "em_birthday", "em_joining_date", "em_contract_end",
                "em_image", "em_nid", "des_id", "dep_id"
            )
        }),
        (_("Permissions"), {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        (_("Important dates"), {"fields": ("last_login",)}),  
    )
    
    # ----------------------------
    # Fieldsets (add user view)
    # ----------------------------
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_active", "is_staff", "is_superuser"),
        }),
    )

    # ----------------------------
    # Search and ordering
    # ----------------------------
    search_fields = ("email", "em_id")
    ordering = ("email",)
    filter_horizontal = ("groups", "user_permissions")
    

# ----------------------------
# Register Models in Admin
# ----------------------------
admin.site.register(User, UserAdmin)
admin.site.register(Department)
admin.site.register(Designation)
