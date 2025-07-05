from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('employee', 'Employee'),
        ('researcher', 'Researcher'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')



    def __str__(self):
        return f"{self.username} ({self.role})"
