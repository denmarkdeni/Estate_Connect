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

    def __str__(self):
        return self.fullname
    
class Dealer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.user.username

class Engineer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    expertise = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    is_approved = models.BooleanField(default=False)
    location = models.CharField(max_length=255,default="")

    def __str__(self):
        return self.user.username


class Property(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ]
    dealer = models.ForeignKey(User, on_delete=models.CASCADE) 
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='property_images/', blank=True, null=True)
    model_3d = models.FileField(upload_to='models/', null=True, blank=True) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    registered_to = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='property_registered')
    sold_to = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='property_sold')

    def __str__(self):
        return self.title

class Inquiry(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('answered', 'Answered'),
        ('read', 'Read'),
        ('closed', 'Closed'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inquiry from {self.customer.user.username} on {self.property.title}"

class PropertyModification(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='modification_requests')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='modifications')
    description = models.TextField()  
    dealer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dealer_requests')
    engineer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='engineer_requests')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} - {self.property.title} ({self.status})"

class AdminReview(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="admin_reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewed_user")
    role = models.CharField(max_length=20, choices=[('dealer', 'Dealer'), ('engineer', 'Engineer')])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"

class FloorPlan(models.Model):
    name = models.CharField(max_length=100)
    svg_data = models.TextField()  # Stores the SVG as text
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name