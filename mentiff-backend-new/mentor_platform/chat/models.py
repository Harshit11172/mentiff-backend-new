from django.db import models
from django.conf import settings


class Group(models.Model):
    group_name = models.CharField(max_length=100)
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='admin_groups')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='group_members', through='Membership')
    college = models.CharField(max_length=255, default="")
    logo = models.ImageField(upload_to='static_files/group_logos/', default = 'static_files/group_logos/mentifflogo.png', null=True, blank=True)  # New logo field
    country = models.CharField(max_length=100)
    url = models.URLField(max_length=200)
    member_count = models.PositiveIntegerField(default=2)  # Member count field
    mentor_count = models.PositiveIntegerField(default=2)   # Mentor count field
    mentee_count = models.PositiveIntegerField(default=2)   # Mentee count field

    def __str__(self):
        return self.college

    def update_member_count(self):
        self.member_count = self.members.count()
        self.save()

    def update_mentor_count(self):
        self.mentor_count = self.members.filter(membership__user_type='mentor').count()
        self.save()

    def update_mentee_count(self):
        self.mentee_count = self.members.filter(membership__user_type='mentee').count()
        self.save()


class Membership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=[
        ('mentor', 'Mentor'),
        ('mentee', 'Mentee'),
        ('admin', 'Admin'),
    ])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.group.update_member_count()
        self.group.update_mentor_count()  # Update mentor count after saving
        self.group.update_mentee_count()   # Update mentee count after saving

    def delete(self, *args, **kwargs):
        group = self.group  # Store the group instance before deletion
        super().delete(*args, **kwargs)
        group.update_member_count()  
        group.update_mentor_count()  # Update mentor count after deletion
        group.update_mentee_count()   # Update mentee count after deletion


class GroupMessage(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)  # Add this line

    