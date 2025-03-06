from django.contrib import admin
from .models import Labour, Skill, Booking, History, Review, UserProfile, Payment
from .custom_admin import admin  # Import the custom admin site

# Labour Admin
@admin.register(Labour)
class LabourAdmin(admin.ModelAdmin):
    list_display = ('user_username', 'phone', 'display_skills', 'experience', 'image', 'email', 'price')
    list_editable = ['price']
    list_filter = ('is_available', 'skills')
    search_fields = ('user__username', 'phone', 'email')
    readonly_fields = ('last_booking_time',)

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Username'

    def display_skills(self, obj):
        return ", ".join(skill.name for skill in obj.skills.all())
    display_skills.short_description = 'Skills'


# UserProfile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'user_email', 'phone', 'address', 'profile_picture')

    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    user_full_name.short_description = 'Full Name'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'


# Payment Admin
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'labour', 'amount', 'status', 'paid', 'created_at')
    list_filter = ('status', 'paid', 'created_at', 'labour')
    search_fields = ('booking_id', 'user__username', 'razorpay_order_id')
    ordering = ('-created_at',)
    list_editable = ('status', 'paid')

    fieldsets = (
        (None, {
            'fields': ('user', 'labour', 'booking_id', 'amount', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'paid', 'status')
        }),
        ('Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )


# Booking Admin
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'labour', 'razorpay_order_id', 'status')
    fields = ('booking_id', 'user', 'labour', 'email', 'amount', 'razorpay_order_id', 'status')


# Skill Admin
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('labour', 'user', 'rating', 'timestamp')  # Use 'timestamp' instead of 'created_at'
    list_filter = ('rating',)
    search_fields = ('labour__user__username', 'user__username')


# History Admin
@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'service', 'details', 'timestamp')
    list_filter = ('action_type', 'service')
    search_fields = ('user__username', 'details')