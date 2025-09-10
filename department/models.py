import uuid
from django.db import models

class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dep_name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.dep_name
