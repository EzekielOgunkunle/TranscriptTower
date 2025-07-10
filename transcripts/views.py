from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views import View
from .forms import TranscriptRequestForm, AdminTranscriptUpdateForm
from .models import TranscriptRequest
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings

# Only allow non-admins to request transcripts
def is_not_admin(user):
    return not user.is_superuser

@method_decorator([login_required, user_passes_test(is_not_admin)], name='dispatch')
class TranscriptRequestCreateView(View):
    def get(self, request):
        form = TranscriptRequestForm()
        return render(request, 'transcripts/request_form.html', {'form': form})

    def post(self, request):
        form = TranscriptRequestForm(request.POST)
        if form.is_valid():
            transcript_request = form.save(commit=False)
            transcript_request.student = request.user
            transcript_request.status = 'pending'
            transcript_request.save()
            messages.info(request, 'Your request has been submitted and is pending admin review. You will be notified when payment is required.')
            return redirect('transcripts:request_list')
        return render(request, 'transcripts/request_form.html', {'form': form})

@method_decorator(login_required, name='dispatch')
class TranscriptRequestListView(View):
    def get(self, request):
        requests = TranscriptRequest.objects.filter(student=request.user).order_by('-created_at')
        return render(request, 'transcripts/request_list.html', {'requests': requests})

@method_decorator(login_required, name='dispatch')
class TranscriptDownloadView(View):
    def get(self, request, pk):
        transcript = TranscriptRequest.objects.get(pk=pk, student=request.user)
        if transcript.pdf_file:
            from django.http import FileResponse
            return FileResponse(transcript.pdf_file.open('rb'), as_attachment=True, filename=f"transcript_{transcript.id}.pdf")
        messages.error(request, 'Transcript file not available.')
        return redirect('transcripts:request_list')

@method_decorator([login_required, user_passes_test(lambda u: u.is_superuser)], name='dispatch')
class AdminTranscriptListView(View):
    def get(self, request):
        requests = TranscriptRequest.objects.all().order_by('-created_at')
        return render(request, 'transcripts/admin_request_list.html', {'requests': requests})

@method_decorator([login_required, user_passes_test(lambda u: u.is_superuser)], name='dispatch')
class AdminTranscriptUpdateView(View):
    def get(self, request, pk):
        transcript = TranscriptRequest.objects.get(pk=pk)
        form = AdminTranscriptUpdateForm(instance=transcript)
        return render(request, 'transcripts/admin_request_update.html', {'form': form, 'transcript': transcript})

    def post(self, request, pk):
        transcript = TranscriptRequest.objects.get(pk=pk)
        form = AdminTranscriptUpdateForm(request.POST, request.FILES, instance=transcript)
        if form.is_valid():
            form.save()
            # If status is set to 'ready_for_payment', notify student
            if transcript.status == 'ready_for_payment':
                from django.core.mail import send_mail
                from django.conf import settings
                from django.template.loader import render_to_string
                email_body = render_to_string('emails/notification_email.html', {
                    'user': transcript.student,
                    'message': f'Your transcript request is ready for payment. The price is: ₦{getattr(transcript, "price", "(set by admin)")}. Please log in to your dashboard to proceed with payment.',
                    'site_name': 'Transcript Tower',
                })
                send_mail(
                    'Transcript Request Ready for Payment',
                    '',
                    settings.DEFAULT_FROM_EMAIL,
                    [transcript.student.email],
                    html_message=email_body,
                    fail_silently=True,
                )
            messages.success(request, 'Transcript request updated!')
            return redirect('transcripts:admin_request_list')
        return render(request, 'transcripts/admin_request_update.html', {'form': form, 'transcript': transcript})

class PaystackPaymentView(View):
    def get(self, request, pk):
        transcript = TranscriptRequest.objects.get(pk=pk)
        paystack_public_key = getattr(settings, 'PAYSTACK_PUBLIC_KEY', '')
        return render(request, 'transcripts/paystack_payment.html', {
            'transcript': transcript,
            'paystack_public_key': paystack_public_key,
        })
