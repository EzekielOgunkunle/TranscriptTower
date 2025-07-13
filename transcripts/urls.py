from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TranscriptRequestCreateView, TranscriptRequestListView, AdminTranscriptListView, AdminTranscriptUpdateView,
    PaystackPaymentView, TranscriptDownloadView, paystack_webhook, contact,
    user_notifications, mark_notification_read, mark_all_notifications_read
)
from .api_views import TranscriptRequestViewSet

app_name = 'transcripts'

router = DefaultRouter()
router.register(r'requests', TranscriptRequestViewSet, basename='transcriptrequest')

urlpatterns = [
    path('request/', TranscriptRequestCreateView.as_view(), name='request_create'),
    path('my-requests/', TranscriptRequestListView.as_view(), name='request_list'),
    path('admin-requests/', AdminTranscriptListView.as_view(), name='admin_request_list'),
    path('admin-requests/<int:pk>/update/', AdminTranscriptUpdateView.as_view(), name='admin_request_update'),
    path('paystack/<int:pk>/', PaystackPaymentView.as_view(), name='paystack_payment'),
    path('download/<int:pk>/', TranscriptDownloadView.as_view(), name='download'),
    path('paystack/webhook/', paystack_webhook, name='paystack_webhook'),
    path('contact/', contact, name='contact'),
    path('notifications/', user_notifications, name='user_notifications'),
    path('notifications/read/<int:pk>/', mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', mark_all_notifications_read, name='mark_all_notifications_read'),
    path('api/', include(router.urls)),
]
