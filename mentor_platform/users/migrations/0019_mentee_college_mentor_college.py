# Generated by Django 5.1.1 on 2024-11-11 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_alter_customuser_verification_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='mentee',
            name='college',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='mentor',
            name='college',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
