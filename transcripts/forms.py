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
        fields = ['status', 'admin_feedback', 'pdf_file', 'payment_confirmed', 'payment_reference', 'price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_reference'].required = False
        self.fields['pdf_file'].required = False
        self.fields['admin_feedback'].required = False
        self.fields['payment_confirmed'].required = False
        self.fields['price'].required = False
        # No manual payment field remains
        # Make payment_confirmed read-only if already confirmed
        if self.instance and self.instance.payment_confirmed:
            self.fields['payment_confirmed'].disabled = True
        # Prevent status changes before 'processing' if payment is confirmed
        if self.instance and self.instance.payment_confirmed:
            allowed_statuses = ['processing', 'pending_review', 'change_requested', 'delivered']
            self.fields['status'].choices = [c for c in self.fields['status'].choices if c[0] in allowed_statuses]

    def clean_pdf_file(self):
        pdf = self.cleaned_data.get('pdf_file')
        if pdf:
            if not pdf.name.lower().endswith('.pdf'):
                raise forms.ValidationError('Only PDF files are allowed.')
            if pdf.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must be under 5MB.')
        return pdf

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
