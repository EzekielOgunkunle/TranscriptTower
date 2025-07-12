from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    dependencies = [
        ('transcripts', '0005_alter_notification_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=30, choices=[
                    ('login', 'Login'),
                    ('logout', 'Logout'),
                    ('create', 'Create'),
                    ('update', 'Update'),
                    ('delete', 'Delete'),
                    ('status_change', 'Status Change'),
                    ('download', 'Download'),
                    ('email', 'Email Notification'),
                    ('admin_action', 'Admin Action'),
                    ('other', 'Other'),
                ])),
                ('object_type', models.CharField(max_length=100)),
                ('object_id', models.CharField(max_length=100, blank=True)),
                ('description', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('extra_data', models.JSONField(blank=True, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
                'verbose_name': 'Activity Log',
                'verbose_name_plural': 'Activity Logs',
            },
        ),
    ]
