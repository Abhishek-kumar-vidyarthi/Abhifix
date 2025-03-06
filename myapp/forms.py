from django import forms
from .models import UserProfile, Labour, Booking

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'profile_picture']


class LabourForm(forms.ModelForm):
    class Meta:
        model = Labour
        fields = ['user', 'phone', 'image', 'skills', 'experience', 'email', 'price', 'is_available', 'last_booking_time']

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['user', 'labour', 'expected_time', 'status', 'amount', 'razorpay_order_id']