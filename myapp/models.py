import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Skill model for defining different skills
class Skill(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Labour model for representing labourers
class Labour(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='labour_profile')
    phone = models.CharField(max_length=15, null=True, blank=True)  # Updated to CharField to handle phone numbers better
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    skills = models.ManyToManyField(Skill, related_name='labours', blank=True)
    experience = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True,blank=True) 
    is_available = models.BooleanField(default=True) 
    last_booking_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username if self.user else "Unnamed Labour"

# UserProfile model for storing additional user information
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, null=True, blank=True)  # Example field for address
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return self.user.username

# Booking model for handling booking details
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    labour = models.ForeignKey('Labour', on_delete=models.CASCADE) 
    email = models.EmailField(max_length=254, null=True, blank=True)
    booking_id = models.CharField(max_length=20, default='', unique=True, editable=False)
    expected_time = models.DateTimeField(default=timezone.now)
    booking_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
    amount = models.IntegerField(default=0)
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)  # Add this field

    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = str(uuid.uuid4())[:5]  # Generate unique 5-character ID
        super(Booking, self).save(*args, **kwargs)

# History model for logging user actions
class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='histories')
    action_type = models.CharField(max_length=100)  # e.g., 'Booking', 'Transaction'
    service = models.CharField(max_length=100, null=True, blank=True)  # Booking service
    details = models.TextField(null=True, blank=True)  # Additional details (optional)
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically sets date and time of the action
    
    def __str__(self):
        return f"{self.user.username} - {self.service} - {self.action_type} - {self.timestamp}"

# Review model for user reviews of labours
class Review(models.Model):
    labour = models.ForeignKey(Labour,on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=0)  # Rating between 0 to 5
    comment = models.TextField(null=True, blank=True)  # Optional comment field
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically sets date and time of the review

    def __str__(self):
        return f"Review by {self.user.username} for {self.labour.user.username} - Rating: {self.rating}"
    

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    labour = models.ForeignKey('Labour', on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, default=1)  # Use ForeignKey here
    amount = models.FloatField()
    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=100, blank=True, null=True)
    paid = models.BooleanField(default=False)
    status = models.CharField(max_length=100,  choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Booking {self.booking.booking_id} by {self.user.username}"
