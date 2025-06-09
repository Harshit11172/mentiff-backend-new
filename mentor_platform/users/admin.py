# users/admin.py

from django.contrib import admin
from .models import CustomUser, Mentor, Mentee, Feedback

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('user_type', 'is_active')

class MentorAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'university', 'degree', 'major', 'expertise', 'session_fee', 'rating')
    search_fields = ('user__username', 'university', 'degree', 'major', 'expertise')
    list_filter = ('expertise', 'rating')

class MenteeAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'university', 'degree', 'major', 'desired_expertise', 'budget')
    search_fields = ('user__username', 'university', 'degree', 'major', 'desired_expertise')
    list_filter = ('desired_expertise',)

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('mentor', 'mentee', 'session_date', 'rating')
    list_filter = ('rating', 'session_date')
    search_fields = ('mentor__user__username', 'mentee__user__username', 'comments')

# Register the models with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Mentor, MentorAdmin)
admin.site.register(Mentee, MenteeAdmin)
admin.site.register(Feedback, FeedbackAdmin)
