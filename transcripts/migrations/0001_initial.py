# Generated by Django 5.2.3 on 2025-06-23 12:53

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TranscriptRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_type', models.CharField(choices=[('soft_copy', 'Soft Copy (PDF via Email)'), ('printed', 'Printed')], max_length=20)),
                ('recipient_name', models.CharField(blank=True, max_length=255)),
                ('recipient_email', models.EmailField(blank=True, max_length=254)),
                ('printed_delivery_method', models.CharField(blank=True, choices=[('pickup', 'Pickup'), ('courier', 'Courier')], max_length=20)),
                ('delivery_address', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('ready_for_payment', 'Ready for Payment'), ('processing', 'Processing'), ('pending_review', 'Pending Review'), ('change_requested', 'Change Requested'), ('confirmed', 'Confirmed'), ('delivered', 'Delivered')], default='pending', max_length=30)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('admin_feedback', models.TextField(blank=True)),
                ('change_requested', models.BooleanField(default=False)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='transcripts/')),
                ('payment_confirmed', models.BooleanField(default=False)),
                ('payment_method', models.CharField(blank=True, max_length=30)),
                ('payment_reference', models.CharField(blank=True, max_length=100)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
