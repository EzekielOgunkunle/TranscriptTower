from django import forms
from .models import TranscriptRequest

class TranscriptRequestForm(forms.ModelForm):
    class Meta:
        model = TranscriptRequest
        fields = [
            'request_type', 'recipient_name', 'recipient_email',
            'printed_delivery_method', 'delivery_address'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recipient_name'].required = False
        self.fields['recipient_email'].required = False
        self.fields['printed_delivery_method'].required = False
        self.fields['delivery_address'].required = False
        if self.data.get('request_type') == TranscriptRequest.SOFT_COPY:
            self.fields['recipient_name'].required = True
            self.fields['recipient_email'].required = True
        elif self.data.get('request_type') == TranscriptRequest.PRINTED:
            self.fields['printed_delivery_method'].required = True
            self.fields['delivery_address'].required = True

class AdminTranscriptUpdateForm(forms.ModelForm):
    class Meta:
        model = TranscriptRequest
        fields = ['status', 'admin_feedback', 'pdf_file', 'payment_confirmed', 'payment_method', 'payment_reference', 'price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].required = False
        self.fields['payment_reference'].required = False
        self.fields['pdf_file'].required = False
        self.fields['admin_feedback'].required = False
        self.fields['payment_confirmed'].required = False
        self.fields['price'].required = False
