from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=255, help_text="Enter your full name as it appears on your ID.")
    matric_number = models.CharField(max_length=20, unique=True)
    graduation_year = models.PositiveIntegerField()
    program = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    current_place = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    REQUIRED_FIELDS = ['email', 'full_name', 'matric_number', 'graduation_year', 'program', 'phone', 'current_place']

    def __str__(self):
        return f"{self.full_name} ({self.matric_number})"

    def save(self, *args, **kwargs):
        # Automatically verify superusers
        if self.is_superuser:
            self.is_verified = True
        super().save(*args, **kwargs)
