from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student Entrepreneur'),
        ('admin', 'Platform Admin'),
        ('manager', 'Business Manager'),
        ('staff', 'Staff')
    ]

    BUSINESS_TYPE_CHOICES = [
        ('digital', 'Digital Products'),
        ('physical', 'Physical Products'),
        ('service', 'Service-based'),
        ('mixed', 'Mixed Business')
    ]

    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
    # Additional profile fields
    business_name = models.CharField(max_length=200, blank=True, null=True)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE_CHOICES, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Student verification
    is_student_verified = models.BooleanField(default=False)
    student_email = models.EmailField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    def is_admin(self):
        return self.role in ['admin', 'manager']

class StudentVerification(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    institution = models.CharField(max_length=200)
    student_id = models.CharField(max_length=50, unique=True)
    verification_document = models.FileField(upload_to='student_verifications/')
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.institution}"