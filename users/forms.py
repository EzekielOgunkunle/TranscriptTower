from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'full_name', 'email', 'matric_number', 'graduation_year', 'program',
            'phone', 'current_place', 'password1', 'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['full_name'].label = 'Full Name (as on your ID card)'
        self.fields['full_name'].help_text = 'Enter your full name exactly as it appears on your official ID. Include all names.'

class OTPVerificationForm(forms.Form):
    otp_code = forms.CharField(max_length=6, label="Enter OTP")

class ResendOTPForm(forms.Form):
    email = forms.EmailField(label="Your registered email")

class CustomPasswordResetForm(PasswordResetForm):
    pass

class CustomSetPasswordForm(SetPasswordForm):
    pass
