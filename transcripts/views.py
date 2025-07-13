# User dashboard notifications view
from .notifications import Notification
from django.contrib.auth.decorators import login_required
from django.db import models
def user_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'transcripts/user_notifications.html', {'notifications': notifications})
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views import View
from .forms import TranscriptRequestForm, AdminTranscriptUpdateForm, ContactForm
from .models import TranscriptRequest
from .notifications import Notification
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
import json
from .audit import ActivityLog

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
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        requests_qs = TranscriptRequest.objects.filter(student=request.user).order_by('-created_at')
        per_page = request.GET.get('per_page', 10)
        try:
            per_page = int(per_page)
            if per_page < 1:
                per_page = 10
        except Exception:
            per_page = 10
        paginator = Paginator(requests_qs, per_page if per_page != 0 else requests_qs.count())
        page = request.GET.get('page')
        try:
            requests_page = paginator.page(page)
        except PageNotAnInteger:
            requests_page = paginator.page(1)
        except EmptyPage:
            requests_page = paginator.page(paginator.num_pages)
        unread_notification_count = Notification.objects.filter(user=request.user, read=False).count()
        # Dashboard summary
        total = requests_qs.count()
        pending = requests_qs.filter(status='pending').count()
        ready = requests_qs.filter(status='ready_for_payment').count()
        delivered = requests_qs.filter(status='delivered').count()
        recent_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        return render(request, 'transcripts/request_list.html', {
            'requests': requests_page,
            'unread_notification_count': unread_notification_count,
            'total_requests': total,
            'pending_requests': pending,
            'ready_requests': ready,
            'delivered_requests': delivered,
            'recent_notifications': recent_notifications,
            'per_page': per_page,
            'paginator': paginator,
        })
# Mark notification as read
@login_required
def mark_notification_read(request, pk):
    notification = Notification.objects.filter(pk=pk, user=request.user).first()
    if notification:
        notification.read = True
        notification.save()
    return redirect('transcripts:user_notifications')

@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    return redirect('transcripts:user_notifications')

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
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        status_filter = request.GET.get('status', '')
        student_query = request.GET.get('student', '').strip()
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        grad_year = request.GET.get('graduation_year', '')
        program = request.GET.get('program', '')
        payment_status = request.GET.get('payment_status', '')
        per_page = request.GET.get('per_page', 10)
        try:
            per_page = int(per_page)
            if per_page < 1:
                per_page = 10
        except Exception:
            per_page = 10
        requests_qs = TranscriptRequest.objects.all()
        if status_filter:
            requests_qs = requests_qs.filter(status=status_filter)
        if student_query:
            requests_qs = requests_qs.filter(
                models.Q(student__username__icontains=student_query) |
                models.Q(student__email__icontains=student_query) |
                models.Q(student__full_name__icontains=student_query) |
                models.Q(matric_number__icontains=student_query)
            )
        if grad_year:
            requests_qs = requests_qs.filter(student__graduation_year=grad_year)
        if program:
            requests_qs = requests_qs.filter(student__program__icontains=program)
        if payment_status:
            if payment_status == 'confirmed':
                requests_qs = requests_qs.filter(payment_confirmed=True)
            elif payment_status == 'pending':
                requests_qs = requests_qs.filter(payment_confirmed=False)
        if date_from:
            requests_qs = requests_qs.filter(created_at__date__gte=date_from)
        if date_to:
            requests_qs = requests_qs.filter(created_at__date__lte=date_to)
        requests_qs = requests_qs.order_by('-created_at')
        paginator = Paginator(requests_qs, per_page if per_page != 0 else requests_qs.count())
        page = request.GET.get('page')
        try:
            requests_page = paginator.page(page)
        except PageNotAnInteger:
            requests_page = paginator.page(1)
        except EmptyPage:
            requests_page = paginator.page(paginator.num_pages)
        # Dashboard summary
        total = TranscriptRequest.objects.count()
        pending = TranscriptRequest.objects.filter(status='pending').count()
        ready = TranscriptRequest.objects.filter(status='ready_for_payment').count()
        confirmed = TranscriptRequest.objects.filter(status='confirmed').count()
        delivered = TranscriptRequest.objects.filter(status='delivered').count()
        manual_payments = TranscriptRequest.objects.filter(status='ready_for_payment', payment_confirmed=False).count()
        # Always show max 5 recent requests (from all, not just filtered)
        recent = TranscriptRequest.objects.order_by('-created_at')[:5]
        return render(request, 'transcripts/admin_request_list.html', {
            'requests': requests_page,
            'total_requests': total,
            'pending_requests': pending,
            'ready_requests': ready,
            'confirmed_requests': confirmed,
            'delivered_requests': delivered,
            'manual_payments': manual_payments,
            'recent_requests': recent,
            'status_filter': status_filter,
            'student_query': student_query,
            'date_from': date_from,
            'date_to': date_to,
            'per_page': per_page,
            'paginator': paginator,
            'graduation_year': grad_year,
            'program': program,
            'payment_status': payment_status,
        })

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
            old_status = transcript.status
            form.save()
            if transcript.status != old_status:
                ActivityLog.objects.create(
                    user=request.user,
                    action='status_change',
                    object_type='TranscriptRequest',
                    object_id=str(transcript.id),
                    description=f"Status changed from {old_status} to {transcript.status}",
                    extra_data={'old_status': old_status, 'new_status': transcript.status}
                )
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
                # Create notification for user
                Notification.objects.create(
                    user=transcript.student,
                    message=f'Your transcript request is ready for payment. The price is: ₦{getattr(transcript, "price", "(set by admin)")}. Please proceed with payment.'
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

@csrf_exempt
def paystack_webhook(request):
    if request.method == 'POST':
        event = json.loads(request.body.decode('utf-8'))
        if event.get('event') == 'charge.success':
            data = event.get('data', {})
            reference = data.get('reference')
            email = data.get('customer', {}).get('email')
            amount = data.get('amount') / 100  # kobo to naira
            # Find transcript by reference
            transcript = TranscriptRequest.objects.filter(payment_reference=reference, student__email=email).first()
            if transcript and not transcript.payment_confirmed:
                transcript.payment_confirmed = True
                transcript.status = 'confirmed'
                transcript.save()
                # Notify user
                email_body = render_to_string('emails/notification_email.html', {
                    'user': transcript.student,
                    'message': f'Your payment of ₦{amount} was successful. Your transcript request is now confirmed.',
                    'site_name': 'Transcript Tower',
                })
                send_mail(
                    'Transcript Payment Confirmed',
                    '',
                    settings.DEFAULT_FROM_EMAIL,
                    [transcript.student.email],
                    html_message=email_body,
                    fail_silently=True,
                )
                # Create notification for user
                Notification.objects.create(
                    user=transcript.student,
                    message=f'Your payment of ₦{amount} was successful. Your transcript request is now confirmed.'
                )
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'ignored'})
    return JsonResponse({'error': 'Invalid method'}, status=405)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def confirm_manual_payment(request, pk):
    transcript = TranscriptRequest.objects.get(pk=pk)
    if request.method == 'POST' and not transcript.payment_confirmed:
        transcript.payment_confirmed = True
        transcript.status = 'confirmed'
        transcript.save()
        # Notify user
        email_body = render_to_string('emails/notification_email.html', {
            'user': transcript.student,
            'message': f'Your manual payment for transcript request #{transcript.id} has been confirmed by admin.',
            'site_name': 'Transcript Tower',
        })
        send_mail(
            'Manual Payment Confirmed',
            '',
            settings.DEFAULT_FROM_EMAIL,
            [transcript.student.email],
            html_message=email_body,
            fail_silently=True,
        )
        # Create notification for user
        Notification.objects.create(
            user=transcript.student,
            message=f'Your manual payment for transcript request #{transcript.id} has been confirmed by admin.'
        )
        messages.success(request, 'Manual payment confirmed and user notified.')
        return redirect('transcripts:admin_request_list')
    return render(request, 'transcripts/confirm_manual_payment.html', {'transcript': transcript})
def contact(request):
    from django.core.mail import send_mail
    from django.conf import settings
    from django.contrib import messages
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            subject = f"Contact Form Submission from {name}"
            body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
            messages.success(request, 'Your message has been sent!')
            return redirect('home')
    else:
        form = ContactForm()
    return render(request, 'home.html', {'form': form})