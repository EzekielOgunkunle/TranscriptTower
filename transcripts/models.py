from django.db import models
from django.conf import settings
from django.utils import timezone
# Import Notification model for migrations

# Create your models here.

class TranscriptRequest(models.Model):
    SOFT_COPY = 'soft_copy'
    PRINTED = 'printed'
    DELIVERY_CHOICES = [
        (SOFT_COPY, 'Soft Copy (PDF via Email)'),
        (PRINTED, 'Printed'),
    ]
    PICKUP = 'pickup'
    COURIER = 'courier'
    PRINTED_DELIVERY_CHOICES = [
        (PICKUP, 'Pickup'),
        (COURIER, 'Courier'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ready_for_payment', 'Ready for Payment'),
        ('processing', 'Processing'),
        ('pending_review', 'Pending Review'),
        ('change_requested', 'Change Requested'),
        ('delivered', 'Delivered'),
    ]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=20, choices=DELIVERY_CHOICES)
    recipient_name = models.CharField(max_length=255, blank=True)
    recipient_email = models.EmailField(blank=True)
    printed_delivery_method = models.CharField(max_length=20, choices=PRINTED_DELIVERY_CHOICES, blank=True)
    delivery_address = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    admin_feedback = models.TextField(blank=True)
    change_requested = models.BooleanField(default=False)
    pdf_file = models.FileField(upload_to='transcripts/', blank=True, null=True)
    payment_confirmed = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


    def __str__(self):
        return f"Transcript Request #{self.id} by {self.student}"


# Timeline/history for each transcript request
class TranscriptRequestTimeline(models.Model):
    request = models.ForeignKey(TranscriptRequest, on_delete=models.CASCADE, related_name='timeline_entries')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=30, blank=True)  # Status at this point (optional)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        who = self.user.full_name if self.user else 'System'
        return f"[{self.created_at:%Y-%m-%d %H:%M}] {who}: {self.status or ''} {self.comment[:30]}"
