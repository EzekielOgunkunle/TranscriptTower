from django.core.management.base import BaseCommand
from transcripts.models import TranscriptRequest
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from transcripts.notifications import Notification
from datetime import timedelta

class Command(BaseCommand):
    help = 'Send payment reminders for transcript requests that are ready for payment but not yet paid.'

    def handle(self, *args, **options):
        now = timezone.now()
        # Remind for requests ready for payment, not paid, and not reminded in last 24h
        cutoff = now - timedelta(hours=24)
        requests = TranscriptRequest.objects.filter(status='ready_for_payment', payment_confirmed=False, updated_at__lt=cutoff)
        count = 0
        for req in requests:
            user = req.student
            email_body = render_to_string('emails/notification_email.html', {
                'user': user,
                'message': f'Reminder: Your transcript request (ID #{req.id}) is ready for payment. Please log in to your dashboard to complete payment.',
                'site_name': 'Transcript Tower',
            })
            send_mail(
                'Payment Reminder: Transcript Request',
                '',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=email_body,
                fail_silently=True,
            )
            Notification.objects.create(
                user=user,
                message=f'Reminder: Your transcript request (ID #{req.id}) is ready for payment. Please complete payment to proceed.'
            )
            req.updated_at = now  # Prevent spamming
            req.save(update_fields=['updated_at'])
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Sent {count} payment reminders.'))
