# users/admin.py

from django.contrib import admin
from .models import CustomUser, Mentor, Mentee, Feedback

from .models import Post, Comment

admin.site.register(Post)
admin.site.register(Comment)

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id','username', 'email', 'user_type', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('user_type', 'is_active')

class MentorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email', 'university', 'degree', 'major', 'expertise', 'rating')
    search_fields = ('user__username', 'university', 'degree', 'major', 'expertise')
    list_filter = ('expertise', 'rating')

    def email(self, obj):
        return obj.user.email
    email.admin_order_field = 'user__email'  # Allow sorting by email
    email.short_description = 'Email'

class MenteeAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'email', 'university', 'degree', 'major', 'desired_expertise', 'budget')
    search_fields = ('user__username', 'university', 'degree', 'major', 'desired_expertise')
    list_filter = ('desired_expertise',)

    def email(self, obj):
        return obj.user.email
    email.admin_order_field = 'user__email'
    email.short_description = 'Email'

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('mentor', 'mentee', 'session_date', 'rating')
    list_filter = ('rating', 'session_date')
    search_fields = ('mentor__user__username', 'mentee__user__username', 'comments')

# Register the models with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Mentor, MentorAdmin)
admin.site.register(Mentee, MenteeAdmin)
admin.site.register(Feedback, FeedbackAdmin)



# admin.py

from django.contrib import admin
from .models import MentorAvailability

@admin.register(MentorAvailability)
class MentorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("mentor", "day_of_week", "start_time", "end_time")
    list_filter = ("day_of_week", "mentor")
    search_fields = ("mentor__user__username",)
    ordering = ("mentor", "day_of_week", "start_time")

            
# from django.contrib import admin
# from .models import Mentor, MentorAvailability

# class MentorAvailabilityInline(admin.TabularInline):
#     model = MentorAvailability
#     extra = 1  # Number of empty rows to show
#     fields = ('day_of_week', 'start_time', 'end_time')
#     ordering = ['day_of_week', 'start_time']


# @admin.register(Mentor)
# class MentorAdmin(admin.ModelAdmin):
#     list_display = ('name',)
#     inlines = [MentorAvailabilityInline]


from django.contrib import admin
from .models import SessionOption

@admin.register(SessionOption)
class SessionOptionAdmin(admin.ModelAdmin):
    list_display = ("id", "mentor_name", "duration_minutes", "fee", "currency")
    search_fields = ("mentor__user__username",)
    list_filter = ("mentor", "currency")

    def mentor_name(self, obj):
        return obj.mentor.user.username
    mentor_name.admin_order_field = "mentor__user__username"
    mentor_name.short_description = "Mentor"
