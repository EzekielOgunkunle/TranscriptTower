from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from .models import CustomUser

class UserRegistrationTests(TestCase):
    def test_user_registration_and_otp_email(self):
        response = self.client.post(reverse('users:register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'matric_number': 'MAT123',
            'graduation_year': 2022,
            'program': 'Computer Science',
            'phone': '1234567890',
            'current_place': 'Lagos',
            'password1': 'Testpass123!',
            'password2': 'Testpass123!'
        })
        self.assertRedirects(response, reverse('users:verify_otp', args=[CustomUser.objects.get(username='testuser').id]))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Your OTP is:', mail.outbox[0].body)

    def test_otp_verification(self):
        from django.utils import timezone
        user = CustomUser.objects.create_user(
            username='otpuser', email='otp@example.com', matric_number='MAT456',
            graduation_year=2023, program='Math', phone='123', current_place='Abuja',
            password='Testpass123!', is_active=False, is_verified=False, otp_code='123456',
            otp_created_at=timezone.now()
        )
        response = self.client.post(reverse('users:verify_otp', args=[user.id]), {'otp_code': '123456'})
        user.refresh_from_db()
        self.assertTrue(user.is_verified)
        self.assertTrue(user.is_active)

    def test_resend_otp(self):
        user = CustomUser.objects.create_user(
            username='resenduser', email='resend@example.com', matric_number='MAT789',
            graduation_year=2024, program='Physics', phone='321', current_place='Kano',
            password='Testpass123!', is_active=False, is_verified=False, otp_code='654321'
        )
        response = self.client.post(reverse('users:resend_otp'), {'email': 'resend@example.com'})
        user.refresh_from_db()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Your new OTP is:', mail.outbox[0].body)
        self.assertNotEqual(user.otp_code, '654321')

class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='resetuser', email='reset@example.com', matric_number='MAT999',
            graduation_year=2025, program='Chemistry', phone='555', current_place='Ibadan',
            password='Testpass123!', is_active=True, is_verified=True
        )

    def test_password_reset_flow(self):
        response = self.client.post(reverse('users:password_reset'), {'email': 'reset@example.com'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Password Reset Requested', mail.outbox[0].body)
