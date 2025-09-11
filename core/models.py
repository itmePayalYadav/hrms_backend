from django.db import models

# ----------------------------
# Base Model
# ----------------------------
class BaseModel(models.Model):
    """
    Abstract base model that provides:
    - created_at: Timestamp when the object is created
    - updated_at: Timestamp when the object is last updated
    - is_deleted: Soft delete flag
    """

    # ----------------------------
    # Timestamps
    # ----------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ----------------------------
    # Soft Delete
    # ----------------------------
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True  # This model will not create its own table
