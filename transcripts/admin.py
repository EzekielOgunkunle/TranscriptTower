from django.contrib import admin
from .models import TranscriptRequest
from .forms import AdminTranscriptUpdateForm
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .audit import ActivityLog
import io
import zipfile
from django.http import HttpResponse

@admin.register(TranscriptRequest)
class TranscriptRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'request_type', 'status', 'graduation_year', 'program', 'created_at', 'payment_confirmed')
    list_filter = ('status', 'request_type', 'payment_confirmed', 'student__graduation_year', 'student__program', 'created_at')
    search_fields = ('student__username', 'student__email', 'student__full_name', 'matric_number', 'recipient_name', 'recipient_email', 'program')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['mark_as_ready_for_payment', 'mark_as_processing', 'mark_as_delivered']
    form = AdminTranscriptUpdateForm

    def mark_as_ready_for_payment(self, request, queryset):
        for req in queryset:
            req.status = 'ready_for_payment'
            req.save()
            # Audit log
            ActivityLog.objects.create(
                user=request.user,
                action='status_change',
                object_type='TranscriptRequest',
                object_id=str(req.id),
                description='Bulk: Marked as ready for payment',
                extra_data={'new_status': 'ready_for_payment'}
            )
            # Notify student
            email_body = render_to_string('emails/notification_email.html', {
                'user': req.student,
                'message': 'Your transcript request is ready for payment. Please log in to complete payment.',
                'site_name': 'Transcript Tower',
            })
            send_mail(
                'Transcript Request Ready for Payment',
                '',
                settings.DEFAULT_FROM_EMAIL,
                [req.student.email],
                html_message=email_body,
                fail_silently=True,
            )
    mark_as_ready_for_payment.short_description = 'Mark selected as Ready for Payment and notify'

    def mark_as_processing(self, request, queryset):
        for req in queryset:
            req.status = 'processing'
            req.save()
            # Audit log
            ActivityLog.objects.create(
                user=request.user,
                action='status_change',
                object_type='TranscriptRequest',
                object_id=str(req.id),
                description='Bulk: Marked as processing',
                extra_data={'new_status': 'processing'}
            )
            # Notify student
            email_body = render_to_string('emails/notification_email.html', {
                'user': req.student,
                'message': 'Your transcript request is now being processed.',
                'site_name': 'Transcript Tower',
            })
            send_mail(
                'Transcript Request Processing',
                '',
                settings.DEFAULT_FROM_EMAIL,
                [req.student.email],
                html_message=email_body,
                fail_silently=True,
            )
    mark_as_processing.short_description = 'Mark selected as Processing and notify'

    def mark_as_delivered(self, request, queryset):
        for req in queryset:
            req.status = 'delivered'
            req.save()
            # Audit log
            ActivityLog.objects.create(
                user=request.user,
                action='status_change',
                object_type='TranscriptRequest',
                object_id=str(req.id),
                description='Bulk: Marked as delivered',
                extra_data={'new_status': 'delivered'}
            )
            # Send notification email if soft copy and PDF uploaded
            if req.request_type == 'soft_copy' and req.pdf_file:
                email_body = render_to_string('emails/notification_email.html', {
                    'user': req.student,
                    'message': 'Your transcript has been delivered. Please check your email or download from your dashboard.',
                    'site_name': 'Transcript Tower',
                })
                send_mail(
                    'Your Transcript is Ready',
                    '',
                    settings.DEFAULT_FROM_EMAIL,
                    [req.student.email],
                    html_message=email_body,
                    fail_silently=True,
                )
    mark_as_delivered.short_description = 'Mark selected as Delivered and notify (soft copy)'

    def send_custom_notification(self, request, queryset):
        for req in queryset:
            mailto_link = f"mailto:{req.student.email}?subject=Transcript%20Notification%20from%20Transcript%20Tower&body=Dear%20{req.student.full_name},%0A%0A[Your%20custom%20message%20here]%0A%0AIf%20this%20is%20a%20soft%20copy%20transcript,%20please%20attach%20the%20PDF%20before%20sending."
            self.message_user(request, f"Mailto link for {req.student.email}: <a href='{mailto_link}' target='_blank'>{mailto_link}</a>", level='info')
            # Audit log
            ActivityLog.objects.create(
                user=request.user,
                action='email',
                object_type='TranscriptRequest',
                object_id=str(req.id),
                description='Bulk: Custom notification generated',
                extra_data={'mailto_link': mailto_link}
            )
    send_custom_notification.short_description = 'Generate mailto link for custom notification (attach PDF manually)'
    actions.append('send_custom_notification')

    def delete_pdf(self, request, queryset):
        for req in queryset:
            if req.pdf_file:
                req.pdf_file.delete(save=True)
                req.pdf_file = None
                req.save()
                # Audit log
                ActivityLog.objects.create(
                    user=request.user,
                    action='update',
                    object_type='TranscriptRequest',
                    object_id=str(req.id),
                    description='Bulk: PDF deleted',
                )
        self.message_user(request, "Selected transcript PDFs deleted. You can now re-upload.")
    delete_pdf.short_description = 'Delete attached PDF(s) for re-upload'
    actions.append('delete_pdf')

    def bulk_download_pdfs(self, request, queryset):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zip_file:
            for req in queryset:
                if req.pdf_file:
                    filename = f"transcript_{req.id}_{req.student.matric_number}.pdf"
                    zip_file.writestr(filename, req.pdf_file.read())
                    # Audit log
                    ActivityLog.objects.create(
                        user=request.user,
                        action='download',
                        object_type='TranscriptRequest',
                        object_id=str(req.id),
                        description='Bulk: PDF downloaded in zip',
                    )
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=transcripts_bulk.zip'
        return response
    bulk_download_pdfs.short_description = 'Download selected PDFs as ZIP'
    actions.append('bulk_download_pdfs')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        ActivityLog.objects.create(
            user=request.user,
            action='update' if change else 'create',
            object_type='TranscriptRequest',
            object_id=str(obj.id),
            description=f"{'Updated' if change else 'Created'} transcript request #{obj.id}",
            extra_data={k: v for k, v in form.cleaned_data.items()}
        )

    def delete_model(self, request, obj):
        ActivityLog.objects.create(
            user=request.user,
            action='delete',
            object_type='TranscriptRequest',
            object_id=str(obj.id),
            description=f"Deleted transcript request #{obj.id}",
        )
        super().delete_model(request, obj)

    def graduation_year(self, obj):
        return obj.student.graduation_year
    graduation_year.admin_order_field = 'student__graduation_year'
    graduation_year.short_description = 'Grad Year'

    def program(self, obj):
        return obj.student.program
    program.admin_order_field = 'student__program'
    program.short_description = 'Program'

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'object_type', 'object_id', 'description')
    list_filter = ('action', 'object_type', 'user')
    search_fields = ('description', 'object_type', 'object_id', 'user__username', 'user__email')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
