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

admin.site.register(Labour, LabourAdmin)
admin.site.register(Skill)
admin.site.register(Booking)
admin.site.register(History)
admin.site.register(Review)
admin.site.register(UserProfile, Myprofile)
