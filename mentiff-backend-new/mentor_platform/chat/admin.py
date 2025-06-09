from django.contrib import admin
from .models import Group, Membership, GroupMessage

class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1  # Number of empty forms to display

class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'group_name', 'get_admins', 'member_count', 'mentor_count', 'mentee_count')
    search_fields = ('group_name', 'college', 'country')
    inlines = [MembershipInline]  # Display memberships inline

    def get_admins(self, obj):
        # Filter admins based on the 'role' field in UserProfile (or your custom model)
        admin_users = obj.admins.filter(user_type='admin')
        print("finding admin")
        print(admin_users)
        print([admin.username for admin in admin_users])
        return ", ".join([admin.username for admin in admin_users])
    
    get_admins.short_description = 'Admins'  # Column header in admin

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('members', 'admins')  # Optimize query


class MembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'group', 'user_type')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'group__group_name')

class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('group', 'sender', 'message', 'timestamp', 'profile_picture')
    list_filter = ('group', 'sender')
    search_fields = ('sender','group')

# Registering the models with the admin site
admin.site.register(Group, GroupAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(GroupMessage, GroupMessageAdmin)
