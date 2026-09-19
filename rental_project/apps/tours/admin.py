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
        return format_html('<span style="font-weight:bold; color:#059669; white-space:nowrap;">{} ج.م</span>', obj.amount)
    amount_display.short_description = "العربون"

    def payment_method_badge(self, obj):
        methods = {
            'instapay': ('#e0e7ff', '#3730a3', 'InstaPay'),
            'vodafone_cash': ('#fee2e2', '#991b1b', 'فودافون كاش'),
            'orange_cash': ('#ffedd5', '#9a3412', 'أورنج كاش'),
        }
        bg, col, text = methods.get(obj.payment_method, ('#f1f5f9', '#334155', obj.get_payment_method_display()))
        return format_html(f'<span style="display:inline-block; white-space:nowrap; background:{bg}; color:{col}; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px;">{text}</span>')
    payment_method_badge.short_description = "وسيلة التحويل"

    def status_badge(self, obj):
        if obj.status == 'approved':
            return format_html('<span style="display:inline-block; white-space:nowrap; background:#dcfce7; color:#15803d; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #bbf7d0;">معتمد ✅</span>')
        elif obj.status == 'rejected':
            return format_html('<span style="display:inline-block; white-space:nowrap; background:#fee2e2; color:#b91c1c; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #fecaca;">مرفوض ❌</span>')
        return format_html('<span style="display:inline-block; white-space:nowrap; background:#fef9c3; color:#854d0e; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #fef08a;">قيد المراجعة ⏳</span>')
    status_badge.short_description = "الحالة"

    def receipt_thumbnail(self, obj):
        if obj.receipt_image:
            return format_html(
                '<a href="{0}" target="_blank" title="اضغط لفتح الصورة الأصلية">'
                '<img src="{0}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px; border: 1px solid #cbd5e1; display: block;" />'
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
                '<img src="{0}" style="max-width: 440px; max-height: 550px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;" />'
                '</a>'
                '<p style="font-size: 11px; color: #64748b; margin-top: 4px;">اضغط على الصورة لفتحها بالحجم الكامل.</p>'
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
                '<a href="{}" style="display:inline-block; white-space:nowrap; background:#16a34a; color:#fff; padding:3px 8px; font-size:11px; font-weight:bold; border-radius:4px; text-decoration:none; margin-left:4px;">قبول ✅</a>'
                '<a href="{}" style="display:inline-block; white-space:nowrap; background:#dc2626; color:#fff; padding:3px 8px; font-size:11px; font-weight:bold; border-radius:4px; text-decoration:none;">رفض ❌</a>',
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
        reason = request.GET.get('reason') or request.POST.get('reason') or "إيصال غير مطابق أو تم إلغاؤه من قبل المشرف."
        receipt.rejection_reason = reason
        receipt.reviewed_by = request.user
        receipt.reviewed_at = timezone.now()
        receipt.save()

        # Update connected TourBooking
        receipt.booking.status = 'rejected'
        receipt.booking.save()

        messages.warning(request, f"تم رفض إيصال الطالب {receipt.booking.full_name} وإلغاء الطلب: ({reason}) ❌")
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
    list_display = (
        'full_name',
        'student_contact',
        'property_title',
        'tour_date',
        'tour_type_badge',
        'deposit_status_badge',
        'booking_status_badge',
        'created_at_short',
    )
    list_filter = ('status', 'tour_type', 'tour_date', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'property__title', 'property__title_ar')
    readonly_fields = ('created_at', 'deposit_details_preview')
    actions = ['confirm_selected_tours', 'cancel_selected_tours']

    fieldsets = (
        ('بيانات الطالب والتواصل', {
            'fields': (('full_name', 'user'), ('phone', 'email'), 'message')
        }),
        ('تفاصيل المعاينة والسكن', {
            'fields': (('property', 'tour_date', 'tour_type'),)
        }),
        ('حالة الحجز والعربون', {
            'fields': ('status', 'deposit_details_preview', 'created_at')
        }),
    )

    def student_contact(self, obj):
        clean_phone = ''.join(c for c in (obj.phone or '') if c.isdigit())
        if clean_phone.startswith('0'):
            clean_phone = '2' + clean_phone
        wa_url = f"https://wa.me/{clean_phone}"
        return format_html(
            '<span style="display:inline-flex; align-items:center; gap:6px; white-space:nowrap;">'
            '<span>{}</span>'
            '<a href="{}" target="_blank" title="مراسلة الطالب على واتساب" style="display:inline-block; text-decoration:none; background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; padding:1px 6px; border-radius:4px; font-size:11px; font-weight:bold;">💬 واتساب</a>'
            '</span>',
            obj.phone, wa_url
        )
    student_contact.short_description = "الهاتف والتواصل"

    def property_title(self, obj):
        if obj.property:
            return obj.property.title_ar or obj.property.title
        return "-"
    property_title.short_description = "السكن المطلوب"

    def tour_type_badge(self, obj):
        if obj.tour_type == 'in_person':
            return format_html('<span style="display:inline-block; white-space:nowrap; background:#f1f5f9; color:#334155; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:bold; border:1px solid #cbd5e1;">🚶‍♂️ ميدانية</span>')
        return format_html('<span style="display:inline-block; white-space:nowrap; background:#ede9fe; color:#6d28d9; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:bold; border:1px solid #ddd6fe;">📹 فيديو</span>')
    tour_type_badge.short_description = "النوع"

    def deposit_status_badge(self, obj):
        if hasattr(obj, 'deposit_receipt'):
            r = obj.deposit_receipt
            receipt_url = reverse('admin:tours_depositreceipt_change', args=[r.id])
            if r.status == 'approved':
                return format_html(
                    '<a href="{}" style="display:inline-block; white-space:nowrap; background:#dcfce7; color:#15803d; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:bold; text-decoration:none; border:1px solid #bbf7d0;" title="عرض الإيصال">'
                    'مدفوع ({} ج.م - {}) ✅'
                    '</a>',
                    receipt_url, r.amount, r.get_payment_method_display()
                )
            elif r.status == 'rejected':
                return format_html(
                    '<a href="{}" style="display:inline-block; white-space:nowrap; background:#fee2e2; color:#b91c1c; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:bold; text-decoration:none; border:1px solid #fecaca;" title="عرض سبب الرفض">'
                    'عربون مرفوض ❌'
                    '</a>',
                    receipt_url
                )
            return format_html(
                '<a href="{}" style="display:inline-block; white-space:nowrap; background:#fef9c3; color:#854d0e; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:bold; text-decoration:none; border:1px solid #fef08a;" title="مراجعة الإيصال">'
                'قيد المراجعة ({} ج.م) ⏳'
                '</a>',
                receipt_url, r.amount
            )
        return format_html('<span style="color:#94a3b8; font-size:11px; white-space:nowrap;">بدون إيصال</span>')
    deposit_status_badge.short_description = "العربون والإيصال"

    def booking_status_badge(self, obj):
        if obj.status == 'confirmed':
            return format_html('<span style="display:inline-block; white-space:nowrap; background:#dcfce7; color:#15803d; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #bbf7d0;">مؤكد ✅</span>')
        elif obj.status == 'pending':
            return format_html('<span style="display:inline-block; white-space:nowrap; background:#fef9c3; color:#854d0e; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #fef08a;">قيد الانتظار ⏳</span>')
        elif obj.status == 'rejected':
            return format_html('<span style="display:inline-block; white-space:nowrap; background:#fee2e2; color:#b91c1c; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #fecaca;">مرفوض ❌</span>')
        elif obj.status == 'completed':
            return format_html('<span style="display:inline-block; white-space:nowrap; background:#f1f5f9; color:#475569; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #cbd5e1;">مكتملة 🏁</span>')
        elif obj.status == 'cancelled':
            return format_html('<span style="display:inline-block; white-space:nowrap; background:#fee2e2; color:#b91c1c; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #fecaca;">ملغية 🚫</span>')
        return obj.get_status_display()
    booking_status_badge.short_description = "حالة المعاينة"

    def created_at_short(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    created_at_short.short_description = "تاريخ الطلب"

    def deposit_details_preview(self, obj):
        if hasattr(obj, 'deposit_receipt'):
            r = obj.deposit_receipt
            receipt_url = reverse('admin:tours_depositreceipt_change', args=[r.id])
            img_html = f'<div style="margin-top:6px;"><a href="{r.receipt_image.url}" target="_blank"><img src="{r.receipt_image.url}" style="max-width:240px; border-radius:6px; border:1px solid #cbd5e1;" /></a></div>' if r.receipt_image else ''
            return format_html(
                '<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px; font-size:12px; max-width:500px;">'
                '<div><strong>المبلغ:</strong> {} ج.م ({})</div>'
                '<div><strong>الحالة:</strong> {}</div>'
                '<div><strong>اسم / رقم المحول:</strong> {}</div>'
                '<div><strong>الرقم المرجعي:</strong> {}</div>'
                '<div><a href="{}" style="color:#0284c7; font-weight:bold;">انتقل لصفحة مراجعة هذا الإيصال ↗</a></div>'
                '{}'
                '</div>',
                r.amount, r.get_payment_method_display(),
                r.get_status_display(),
                r.sender_info or '-',
                r.reference_number or '-',
                receipt_url,
                format_html(img_html)
            )
        return "لا يوجد إيصال عربون مرتبط بهذا الحجز."
    deposit_details_preview.short_description = "بيانات إيصال العربون المرفق"

    def confirm_selected_tours(self, request, queryset):
        count = queryset.update(status='confirmed')
        messages.success(request, f"تم تأكيد {count} موعد معاينة بنجاح ✅")
    confirm_selected_tours.short_description = "تأكيد مواعيد المعاينة المحددة ✅"

    def cancel_selected_tours(self, request, queryset):
        count = queryset.update(status='cancelled')
        messages.warning(request, f"تم إلغاء {count} موعد معاينة 🚫")
    cancel_selected_tours.short_description = "إلغاء مواعيد المعاينة المحددة 🚫"
