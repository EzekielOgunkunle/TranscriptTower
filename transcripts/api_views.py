from rest_framework import viewsets, permissions
from .models import TranscriptRequest
from .api_serializers import TranscriptRequestSerializer

class TranscriptRequestViewSet(viewsets.ModelViewSet):
    serializer_class = TranscriptRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users see only their own requests; admins see all
        user = self.request.user
        if user.is_superuser:
            return TranscriptRequest.objects.all()
        return TranscriptRequest.objects.filter(student=user)
