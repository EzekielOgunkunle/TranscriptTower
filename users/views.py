from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.views import View
from .forms import CustomUserCreationForm, OTPVerificationForm, ResendOTPForm, CustomPasswordResetForm, CustomSetPasswordForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
import random

User = get_user_model()

def generate_otp():
    return str(random.randint(100000, 999999))

class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'users/register.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.otp_code = generate_otp()
            user.otp_created_at = timezone.now()
            user.save()
            # Send OTP email
            send_mail(
                'Your Transcript Tower OTP',
                f'Your OTP is: {user.otp_code}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            messages.success(request, 'Registration successful! Check your email for the OTP.')
            # Do not log in yet; only after verification
            return redirect('users:verify_otp', user_id=user.id)
        return render(request, 'users/register.html', {'form': form})

class OTPVerifyView(View):
    def get(self, request, user_id):
        form = OTPVerificationForm()
        return render(request, 'users/verify_otp.html', {'form': form, 'user_id': user_id})

    def post(self, request, user_id):
        form = OTPVerificationForm(request.POST)
        user = User.objects.get(id=user_id)
        if form.is_valid():
            otp = form.cleaned_data['otp_code']
            if user.otp_code == otp and user.otp_created_at and (timezone.now() - user.otp_created_at).seconds < 600:
                user.is_verified = True
                user.is_active = True
                user.otp_code = None
                user.save()
                login(request, user)
                messages.success(request, 'Account verified! You are now signed in.')
                # Redirect to dashboard, not verified_only
                if user.is_superuser:
                    return redirect('transcripts:admin_request_list')
                else:
                    return redirect('transcripts:request_list')
            else:
                messages.error(request, 'Invalid or expired OTP.')
        return render(request, 'users/verify_otp.html', {'form': form, 'user_id': user_id})

class ResendOTPView(View):
    def get(self, request):
        form = ResendOTPForm()
        return render(request, 'users/resend_otp.html', {'form': form})

    def post(self, request):
        form = ResendOTPForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email, is_verified=False)
                user.otp_code = generate_otp()
                user.otp_created_at = timezone.now()
                user.save()
                send_mail(
                    'Your new Transcript Tower OTP',
                    f'Your new OTP is: {user.otp_code}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, 'A new OTP has been sent to your email.')
                return redirect('users:verify_otp', user_id=user.id)
            except User.DoesNotExist:
                messages.error(request, 'No unverified user found with that email.')
        return render(request, 'users/resend_otp.html', {'form': form})

from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = '/users/password-reset/done/'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'users/password_reset_confirm.html'
    success_url = '/users/password-reset/complete/'

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_verified:
            messages.error(self.request, 'You must verify your account before signing in.')
            return redirect('users:resend_otp')
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    next_page = '/users/login/'

# Decorator to restrict actions to verified users or admins
verified_or_admin = user_passes_test(lambda u: u.is_verified or u.is_superuser, login_url='/users/login/')

# Example of a protected view
@method_decorator([login_required, verified_or_admin], name='dispatch')
class VerifiedOnlyView(View):
    def get(self, request):
        return render(request, 'users/verified_only.html')

@login_required
def dashboard_redirect(request):
    if request.user.is_superuser:
        return redirect('transcripts:admin_request_list')
    elif request.user.is_verified:
        return redirect('transcripts:request_list')
    else:
        return redirect('users:resend_otp')
