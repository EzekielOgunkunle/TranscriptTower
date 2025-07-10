from django.urls import path
from .views import TranscriptRequestCreateView, TranscriptRequestListView, AdminTranscriptListView, AdminTranscriptUpdateView
from .views import PaystackPaymentView, TranscriptDownloadView, paystack_webhook, confirm_manual_payment

app_name = 'transcripts'

urlpatterns = [
    path('request/', TranscriptRequestCreateView.as_view(), name='request_create'),
    path('my-requests/', TranscriptRequestListView.as_view(), name='request_list'),
    path('admin-requests/', AdminTranscriptListView.as_view(), name='admin_request_list'),
    path('admin-requests/<int:pk>/update/', AdminTranscriptUpdateView.as_view(), name='admin_request_update'),
    path('admin-requests/<int:pk>/confirm-payment/', confirm_manual_payment, name='confirm_manual_payment'),
    path('paystack/<int:pk>/', PaystackPaymentView.as_view(), name='paystack_payment'),
    path('download/<int:pk>/', TranscriptDownloadView.as_view(), name='download'),
    path('paystack/webhook/', paystack_webhook, name='paystack_webhook'),
]
