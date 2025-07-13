from rest_framework import serializers
from .models import TranscriptRequest, TranscriptRequestTimeline

class TranscriptRequestTimelineSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    class Meta:
        model = TranscriptRequestTimeline
        fields = ['id', 'created_at', 'user_full_name', 'status', 'comment']

class TranscriptRequestSerializer(serializers.ModelSerializer):
    timeline_entries = TranscriptRequestTimelineSerializer(many=True, read_only=True)
    class Meta:
        model = TranscriptRequest
        fields = [
            'id', 'student', 'request_type', 'recipient_name', 'recipient_email',
            'printed_delivery_method', 'delivery_address', 'status', 'created_at',
            'updated_at', 'admin_feedback', 'change_requested', 'pdf_file',
            'payment_confirmed', 'payment_method', 'payment_reference', 'price',
            'timeline_entries'
        ]
