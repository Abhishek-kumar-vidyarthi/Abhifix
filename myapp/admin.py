from django.contrib import admin
from .models import Labour, Skill, Booking, History, Review, UserProfile

class LabourAdmin(admin.ModelAdmin):
    list_display = ('user_username', 'phone', 'display_skills', 'experience', 'image', 'email', 'price')
    list_editable = ['price'] 

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Username'

    def display_skills(self, obj):
        return ", ".join(skill.name for skill in obj.skills.all())
    display_skills.short_description = 'Skills'

class Myprofile(admin.ModelAdmin):
    list_display = ('user_full_name', 'user_email', 'phone', 'address', 'profile_picture')

    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    user_full_name.short_description = 'Full Name'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

from django.contrib import admin
from .models import Payment

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'labour', 'amount', 'status', 'paid', 'created_at')
    list_filter = ('status', 'paid', 'created_at', 'labour')
    search_fields = ('booking_id', 'user__username', 'razorpay_order_id')
    ordering = ('-created_at',)
    list_editable = ('status', 'paid')
    
    # Optionally, you can create fieldsets for better form layout in the admin
    fieldsets = (
        (None, {
            'fields': ('user', 'labour', 'booking_id', 'amount', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'paid', 'status')
        }),
        ('Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'labour', 'razorpay_order_id', 'status')
    fields = ('booking_id', 'user', 'labour', 'email', 'amount', 'razorpay_order_id', 'status')

admin.site.register(Payment, PaymentAdmin)


















admin.site.register(Labour, LabourAdmin)
admin.site.register(Skill)
admin.site.register(Booking)
admin.site.register(History)
admin.site.register(Review)
admin.site.register(UserProfile, Myprofile)
