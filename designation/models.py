import uuid
from django.db import models
from department.models import Department

class Designation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    des_name = models.CharField(max_length=64)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="designations",
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ("des_name", "department")

    def __str__(self):
        return f"{self.des_name} ({self.department.dep_name if self.department else 'No Dept'})"
