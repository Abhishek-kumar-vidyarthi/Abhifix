from django.contrib import admin
from .models import Labour, Skill,Booking, History,Review,UserProfile

class LabourAdmin(admin.ModelAdmin):
    list_display = ('user_username', 'phone', 'display_skills', 'experience', 'image','email')

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Username'

    def display_skills(self, obj):
        return ", ".join(skill.name for skill in obj.skills.all())
    display_skills.short_description = 'Skills'

admin.site.register(Labour, LabourAdmin)
admin.site.register(Skill)  # Ensure this is the correct model registration
admin.site.register(Booking)
admin.site.register(History)
admin.site.register(Review)
admin.site.register(UserProfile)
