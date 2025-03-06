from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from .models import Labour, Booking, User

class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard), name='dashboard'),
        ]
        return custom_urls + urls

    def dashboard(self, request):
        # Add custom logic here
        context = {
            'total_labours': Labour.objects.count(),
            'total_bookings': Booking.objects.count(),
            'total_users': User.objects.count(),
        }
        return render(request, 'admin/dashboard.html', context)

# Replace the default admin site
admin.site = CustomAdminSite(name='myadmin')