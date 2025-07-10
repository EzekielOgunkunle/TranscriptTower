from django.urls import path
from .views import RegisterView, OTPVerifyView, ResendOTPView, CustomPasswordResetView, CustomPasswordResetConfirmView, CustomLoginView, CustomLogoutView, VerifiedOnlyView, dashboard_redirect

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('dashboard/', dashboard_redirect, name='dashboard'),
    path('verify-otp/<int:user_id>/', OTPVerifyView.as_view(), name='verify_otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('verified-only/', VerifiedOnlyView.as_view(), name='verified_only'),
]
