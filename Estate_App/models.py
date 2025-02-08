from django.db import models
from django.contrib.auth.models import User

class UserInfo(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('dealer', 'Dealer'),
        ('customer', 'Customer'),
        ('engineer', 'Engineer'),
    ]
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    fullname = models.CharField(max_length=150)
    UserRole = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.fullname