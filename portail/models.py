# portail/models.py
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ("manager", "Manager"),
        ("employee", "Employee"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    odoo_employee_id = models.IntegerField(null=True, blank=True)
    force_password_change = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="employee")  # ✅ جديد
