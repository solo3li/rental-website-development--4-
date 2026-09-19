from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import TourBooking, DepositReceipt, PaymentSettings

@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'deposit_amount_egp', 'instapay_address', 'vodafone_cash_number', 'is_deposit_required', 'updated_at')
    fieldsets = (
        ('حالة الخدمة وقيمة العربون', {
            'fields': (
                ('is_deposit_required', 'deposit_amount_egp'),
            ),
            'description': 'يمكنك تفعيل أو إيقاف إلزامية دفع العربون وتحديد قيمته الثابتة بالجنيه المصري.'
        }),
        ('بيانات الحسابات والمحافظ للتحويل', {
            'fields': (
                ('instapay_address', 'instapay_account_name'),
                ('vodafone_cash_number', 'orange_cash_number'),
            ),
            'description': 'هذه البيانات تظهر للطالب تلقائياً في نافذة السداد عند حجز المعاينة مع زر نسخ سريع.'
        }),
        ('تعليمات الدفع للطلاب', {
            'fields': ('payment_instructions',),
        }),
    )

    def has_add_permission(self, request):
        # Only allow 1 instance
        if PaymentSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DepositReceipt)
class DepositReceiptAdmin(admin.ModelAdmin):
    list_display = (
        'receipt_thumbnail',
        'student_name',
        'property_link',
        'amount_display',
        'payment_method_badge',
        'sender_info',
        'status_badge',
        'created_at_display',
        'quick_actions',
    )
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('booking__full_name', 'booking__phone', 'booking__email', 'sender_info', 'reference_number', 'booking__property__title')
    readonly_fields = ('receipt_large_preview', 'created_at', 'reviewed_by', 'reviewed_at')
    actions = ['approve_selected', 'reject_selected']

    fieldsets = (
        ('بيانات المعاينة والطالب', {
            'fields': ('booking',),
        }),
        ('تفاصيل التحويل والمبلغ', {
            'fields': (
                ('amount', 'payment_method'),
                ('sender_info', 'reference_number'),
            )
        }),
        ('إيصال التحويل (Screenshot)', {
            'fields': ('receipt_image', 'receipt_large_preview'),
        }),
        ('حالة المراجعة والاعتماد', {
            'fields': (
                'status',
                'rejection_reason',
                ('reviewed_by', 'reviewed_at'),
                'created_at',
            )
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:receipt_id>/approve/', self.admin_site.admin_view(self.approve_receipt_view), name='tours_depositreceipt_approve'),
            path('<int:receipt_id>/reject/', self.admin_site.admin_view(self.reject_receipt_view), name='tours_depositreceipt_reject'),
        ]
        return custom_urls + urls

    def student_name(self, obj):
        return f"{obj.booking.full_name} ({obj.booking.phone})"
    student_name.short_description = "الطالب والهاتف"

    def property_link(self, obj):
        if obj.booking and obj.booking.property:
            return obj.booking.property.title_ar or obj.booking.property.title
        return "-"
    property_link.short_description = "السكن المطلوب"

    def amount_display(self, obj):
        return format_html('<span style="font-weight:bold; color:#059669;">{} ج.م</span>', obj.amount)
    amount_display.short_description = "العربون"

    def payment_method_badge(self, obj):
        methods = {
            'instapay': ('#e0e7ff', '#4338ca', 'InstaPay'),
            'vodafone_cash': ('#fee2e2', '#b91c1c', 'فودافون كاش'),
            'orange_cash': ('#ffedd5', '#c2410c', 'أورنج كاش'),
        }
        bg, col, text = methods.get(obj.payment_method, ('#f1f5f9', '#475569', obj.get_payment_method_display()))
        return format_html(f'<span style="background:{bg}; color:{col}; padding:3px 8px; border-radius:12px; font-weight:bold; font-size:11px;">{text}</span>')
    payment_method_badge.short_description = "وسيلة التحويل"

    def status_badge(self, obj):
        if obj.status == 'approved':
            return format_html('<span style="background:#dcfce7; color:#15803d; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:11px;">معتمد ✅</span>')
        elif obj.status == 'rejected':
            return format_html('<span style="background:#fee2e2; color:#b91c1c; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:11px;">مرفوض ❌</span>')
        return format_html('<span style="background:#fef9c3; color:#a16207; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:11px;">قيد المراجعة ⏳</span>')
    status_badge.short_description = "الحالة"

    def receipt_thumbnail(self, obj):
        if obj.receipt_image:
            return format_html(
                '<a href="{0}" target="_blank" title="اضغط للتكبير" onclick="window.open(\'{0}\', \'_blank\', \'width=900,height=1000\'); return false;">'
                '<img src="{0}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px; border: 2px solid #cbd5e1; box-shadow: 0 1px 3px rgba(0,0,0,0.1);" />'
                '</a>',
                obj.receipt_image.url
            )
        return "-"
    receipt_thumbnail.short_description = "الإيصال"

    def receipt_large_preview(self, obj):
        if obj.receipt_image:
            return format_html(
                '<div style="margin-top: 8px;">'
                '<a href="{0}" target="_blank">'
                '<img src="{0}" style="max-width: 480px; max-height: 600px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.15); border: 1px solid #e2e8f0;" />'
                '</a>'
                '<p style="font-size: 11px; color: #64748b; margin-top: 4px;">اضغط على الصورة لفتحها بالحجم الأصلي الكامل.</p>'
                '</div>',
                obj.receipt_image.url
            )
        return "لا توجد صورة مرفوعة"
    receipt_large_preview.short_description = "معاينة الإيصال مكبرة"

    def created_at_display(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    created_at_display.short_description = "تاريخ الإرسال"

    def quick_actions(self, obj):
        if obj.status == 'pending':
            approve_url = reverse('admin:tours_depositreceipt_approve', args=[obj.id])
            reject_url = reverse('admin:tours_depositreceipt_reject', args=[obj.id])
            return format_html(
                '<a class="button" style="background:#16a34a; color:#fff; padding:4px 8px; font-size:11px; font-weight:bold; border-radius:6px; text-decoration:none; margin-right:4px;" href="{}">قبول ✅</a>'
                '<a class="button" style="background:#dc2626; color:#fff; padding:4px 8px; font-size:11px; font-weight:bold; border-radius:6px; text-decoration:none;" href="{}">رفض ❌</a>',
                approve_url, reject_url
            )
        return "-"
    quick_actions.short_description = "قرار سريع"

    def approve_receipt_view(self, request, receipt_id):
        receipt = get_object_or_404(DepositReceipt, pk=receipt_id)
        receipt.status = 'approved'
        receipt.reviewed_by = request.user
        receipt.reviewed_at = timezone.now()
        receipt.save()

        # Update connected TourBooking
        receipt.booking.status = 'confirmed'
        receipt.booking.save()

        messages.success(request, f"تم اعتماد إيصال الطالب {receipt.booking.full_name} وتأكيد موعد المعاينة بنجاح ✅")
        return redirect('admin:tours_depositreceipt_changelist')

    def reject_receipt_view(self, request, receipt_id):
        receipt = get_object_or_404(DepositReceipt, pk=receipt_id)
        receipt.status = 'rejected'
        receipt.rejection_reason = "إيصال غير مطابق أو تم إلغاؤه من قبل المشرف."
        receipt.reviewed_by = request.user
        receipt.reviewed_at = timezone.now()
        receipt.save()

        # Update connected TourBooking
        receipt.booking.status = 'rejected'
        receipt.booking.save()

        messages.warning(request, f"تم رفض إيصال الطالب {receipt.booking.full_name} وإلغاء الطلب ❌")
        return redirect('admin:tours_depositreceipt_changelist')

    def approve_selected(self, request, queryset):
        for r in queryset:
            r.status = 'approved'
            r.reviewed_by = request.user
            r.reviewed_at = timezone.now()
            r.save()
            r.booking.status = 'confirmed'
            r.booking.save()
        messages.success(request, f"تم اعتماد {queryset.count()} إيصال وتأكيد حجوزاتهم بنجاح.")
    approve_selected.short_description = "اعتماد الإيصالات المحددة وتأكيد الحجز ✅"

    def reject_selected(self, request, queryset):
        for r in queryset:
            r.status = 'rejected'
            r.rejection_reason = "تم الرفض بواسطة المشرف."
            r.reviewed_by = request.user
            r.reviewed_at = timezone.now()
            r.save()
            r.booking.status = 'rejected'
            r.booking.save()
        messages.warning(request, f"تم رفض {queryset.count()} إيصال وإلغاء طلباتهم.")
    reject_selected.short_description = "رفض الإيصالات المحددة وإلغاء الطلبات ❌"


@admin.register(TourBooking)
class TourBookingAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'property', 'tour_date', 'tour_type', 'phone', 'deposit_status', 'status', 'created_at')
    list_filter = ('status', 'tour_type', 'tour_date')
    search_fields = ('full_name', 'email', 'phone', 'property__title')
    readonly_fields = ('created_at',)

    def deposit_status(self, obj):
        if hasattr(obj, 'deposit_receipt'):
            r = obj.deposit_receipt
            if r.status == 'approved':
                return format_html('<span style="color:#15803d; font-weight:bold;">مدفوع ومعتمد ({0} ج.م)</span>', r.amount)
            elif r.status == 'rejected':
                return format_html('<span style="color:#b91c1c; font-weight:bold;">عربون مرفوض</span>')
            return format_html('<a href="{0}" style="color:#a16207; font-weight:bold; text-decoration:underline;">إيصال قيد المراجعة ⏳</a>', reverse('admin:tours_depositreceipt_change', args=[r.id]))
        return format_html('<span style="color:#94a3b8;">بدون إيصال</span>')
    deposit_status.short_description = "حالة العربون"
