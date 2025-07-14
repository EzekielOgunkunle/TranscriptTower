from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.contrib.auth import get_user_model
from .models import TranscriptRequest

User = get_user_model()

class TranscriptRequestTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student', email='student@example.com', password='Testpass123!',
            matric_number='MAT001', graduation_year=2022, program='CS', phone='123', current_place='Lagos', is_verified=True
        )
        self.admin = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='Adminpass123!',
            matric_number='ADMIN', graduation_year=2000, program='Admin', phone='000', current_place='HQ'
        )

    def test_student_can_submit_soft_copy_request(self):
        self.client.login(username='student', password='Testpass123!')
        response = self.client.post(reverse('transcripts:request_create'), {
            'request_type': 'soft_copy',
            'recipient_name': 'Recipient',
            'recipient_email': 'rec@example.com',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TranscriptRequest.objects.filter(student=self.user, request_type='soft_copy').exists())

    def test_student_can_submit_printed_request(self):
        self.client.login(username='student', password='Testpass123!')
        response = self.client.post(reverse('transcripts:request_create'), {
            'request_type': 'printed',
            'printed_delivery_method': 'pickup',
            'delivery_address': '123 Main St',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TranscriptRequest.objects.filter(student=self.user, request_type='printed').exists())

    def test_admin_can_update_status_and_upload_pdf(self):
        req = TranscriptRequest.objects.create(
            student=self.user, request_type='soft_copy', status='processing'
        )
        self.client.login(username='admin', password='Adminpass123!')
        pdf = SimpleUploadedFile('transcript.pdf', b'PDF content', content_type='application/pdf')
        response = self.client.post(reverse('transcripts:admin_request_update', args=[req.id]), {
            'status': 'delivered',
            'admin_feedback': 'Done',
            'pdf_file': pdf,
            'payment_confirmed': True,
            'payment_reference': 'REF123',
        })  # payment_confirmed is now read-only, but test keeps for legacy compatibility
        req.refresh_from_db()
        self.assertEqual(req.status, 'delivered')
        self.assertTrue(req.pdf_file)

    def test_student_can_download_pdf(self):
        req = TranscriptRequest.objects.create(
            student=self.user, request_type='soft_copy', status='delivered'
        )
        req.pdf_file.save('transcript.pdf', SimpleUploadedFile('transcript.pdf', b'PDF content', content_type='application/pdf'))
        self.client.login(username='student', password='Testpass123!')
        response = self.client.get(reverse('transcripts:download', args=[req.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_notifications_sent_on_status_change(self):
        req = TranscriptRequest.objects.create(
            student=self.user, request_type='soft_copy', status='pending'
        )
        self.client.login(username='admin', password='Adminpass123!')
        # Mark as ready for payment
        admin = User.objects.get(username='admin')
        self.client.post(reverse('admin:transcripts_transcriptrequest_changelist'), {'action': 'mark_as_ready_for_payment', '_selected_action': [req.id]})
        self.assertTrue(any('ready for payment' in m.subject.lower() for m in mail.outbox))
