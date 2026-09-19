from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from apps.core.i18n import _bi, is_arabic
from .models import TourBooking, DepositReceipt, PaymentSettings

@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'deposit_amount_egp', 'instapay_address', 'vodafone_cash_number', 'is_deposit_required', 'updated_at')
    fieldsets = (
        (_bi('حالة الخدمة وقيمة العربون', 'Service Status & Deposit Amount'), {
            'fields': (
                ('is_deposit_required', 'deposit_amount_egp'),
            ),
            'description': _bi(
                'يمكنك تفعيل أو إيقاف إلزامية دفع العربون وتحديد قيمته الثابتة بالجنيه المصري.',
                'Configure whether deposit is required and set the fixed amount in EGP.'
            )
        }),
        (_bi('بيانات الحسابات والمحافظ للتحويل', 'Transfer Accounts & Wallets'), {
            'fields': (
                ('instapay_address', 'instapay_account_name'),
                ('vodafone_cash_number', 'orange_cash_number'),
            ),
            'description': _bi(
                'هذه البيانات تظهر للطالب تلقائياً في نافذة السداد عند حجز المعاينة مع زر نسخ سريع.',
                'These payment details are shown to the student automatically during booking.'
            )
        }),
        (_bi('تعليمات الدفع للطلاب', 'Payment Instructions for Students'), {
            'fields': ('payment_instructions',),
        }),
    )

    def has_add_permission(self, request):
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
        (_bi('بيانات المعاينة والطالب', 'Tour & Student Information'), {
            'fields': ('booking',),
        }),
        (_bi('تفاصيل التحويل والمبلغ', 'Transfer Details & Amount'), {
            'fields': (
                ('amount', 'payment_method'),
                ('sender_info', 'reference_number'),
            )
        }),
        (_bi('إيصال التحويل (Screenshot)', 'Receipt Screenshot'), {
            'fields': ('receipt_image', 'receipt_large_preview'),
        }),
        (_bi('حالة المراجعة والاعتماد', 'Review Status & Decision'), {
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
    student_name.short_description = _bi("الطالب والهاتف", "Student & Phone")

    def property_link(self, obj):
        if obj.booking and obj.booking.property:
            return obj.booking.property.title_ar or obj.booking.property.title
        return "-"
    property_link.short_description = _bi("السكن المطلوب", "Property")

    def amount_display(self, obj):
        ar = is_arabic()
        currency = "ج.م" if ar else "EGP"
        return format_html('<span style="font-weight:bold; color:#059669; white-space:nowrap !important;">{} {}</span>', obj.amount, currency)
    amount_display.short_description = _bi("العربون", "Deposit")

    def payment_method_badge(self, obj):
        ar = is_arabic()
        methods = {
            'instapay': ('#e0e7ff', '#3730a3', 'InstaPay'),
            'vodafone_cash': ('#fee2e2', '#991b1b', 'فودافون كاش' if ar else 'Vodafone Cash'),
            'orange_cash': ('#ffedd5', '#9a3412', 'أورنج كاش' if ar else 'Orange Cash'),
        }
        bg, col, text = methods.get(obj.payment_method, ('#f1f5f9', '#334155', obj.get_payment_method_display()))
        return format_html(f'<span style="display:inline-block; white-space:nowrap !important; background:{bg}; color:{col}; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px;">{text}</span>')
    payment_method_badge.short_description = _bi("وسيلة التحويل", "Payment Method")

    def status_badge(self, obj):
        ar = is_arabic()
        if obj.status == 'approved':
            label = 'معتمد ✅' if ar else 'Approved ✅'
            return format_html(f'<span style="display:inline-block; white-space:nowrap !important; background:#dcfce7; color:#15803d; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #bbf7d0;">{label}</span>')
        elif obj.status == 'rejected':
            label = 'مرفوض ❌' if ar else 'Rejected ❌'
            return format_html(f'<span style="display:inline-block; white-space:nowrap !important; background:#fee2e2; color:#b91c1c; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #fecaca;">{label}</span>')
        label = 'قيد المراجعة ⏳' if ar else 'Pending Review ⏳'
        return format_html(f'<span style="display:inline-block; white-space:nowrap !important; background:#fef9c3; color:#854d0e; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #fef08a;">{label}</span>')
    status_badge.short_description = _bi("الحالة", "Status")

    def receipt_thumbnail(self, obj):
        ar = is_arabic()
        if obj.receipt_image:
            tooltip = "اضغط لفتح الصورة الأصلية" if ar else "Click to open full image"
            return format_html(
                '<a href="{0}" target="_blank" title="{1}">'
                '<img src="{0}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px; border: 1px solid #cbd5e1; display: block;" />'
                '</a>',
                obj.receipt_image.url, tooltip
            )
        return "-"
    receipt_thumbnail.short_description = _bi("الإيصال", "Receipt")

    def receipt_large_preview(self, obj):
        ar = is_arabic()
        if obj.receipt_image:
            tip = "اضغط على الصورة لفتحها بالحجم الكامل." if ar else "Click image to open in full resolution."
            return format_html(
                '<div style="margin-top: 8px;">'
                '<a href="{0}" target="_blank">'
                '<img src="{0}" style="max-width: 440px; max-height: 550px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;" />'
                '</a>'
                '<p style="font-size: 11px; color: #64748b; margin-top: 4px;">{}</p>'
                '</div>',
                obj.receipt_image.url, tip
            )
        return "لا توجد صورة مرفوعة" if ar else "No uploaded receipt image"
    receipt_large_preview.short_description = _bi("معاينة الإيصال مكبرة", "Large Receipt Preview")

    def created_at_display(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    created_at_display.short_description = _bi("تاريخ الإرسال", "Submission Date")

    def quick_actions(self, obj):
        ar = is_arabic()
        if obj.status == 'pending':
            approve_url = reverse('admin:tours_depositreceipt_approve', args=[obj.id])
            reject_url = reverse('admin:tours_depositreceipt_reject', args=[obj.id])
            appr_lbl = "قبول ✅" if ar else "Approve ✅"
            rej_lbl = "رفض ❌" if ar else "Reject ❌"
            return format_html(
                '<a href="{}" style="display:inline-block; white-space:nowrap !important; background:#16a34a; color:#fff; padding:3px 8px; font-size:11px; font-weight:bold; border-radius:4px; text-decoration:none; margin-inline-end:4px;">{}</a>'
                '<a href="{}" style="display:inline-block; white-space:nowrap !important; background:#dc2626; color:#fff; padding:3px 8px; font-size:11px; font-weight:bold; border-radius:4px; text-decoration:none;">{}</a>',
                approve_url, appr_lbl, reject_url, rej_lbl
            )
        return "-"
    quick_actions.short_description = _bi("قرار سريع", "Quick Decision")

    def approve_receipt_view(self, request, receipt_id):
        ar = is_arabic()
        receipt = get_object_or_404(DepositReceipt, pk=receipt_id)
        receipt.status = 'approved'
        receipt.reviewed_by = request.user
        receipt.reviewed_at = timezone.now()
        receipt.save()

        receipt.booking.status = 'confirmed'
        receipt.booking.save()

        msg = f"تم اعتماد إيصال الطالب {receipt.booking.full_name} وتأكيد موعد المعاينة بنجاح ✅" if ar else f"Receipt for {receipt.booking.full_name} approved and tour confirmed ✅"
        messages.success(request, msg)
        return redirect('admin:tours_depositreceipt_changelist')

    def reject_receipt_view(self, request, receipt_id):
        ar = is_arabic()
        receipt = get_object_or_404(DepositReceipt, pk=receipt_id)
        receipt.status = 'rejected'
        reason = request.GET.get('reason') or request.POST.get('reason') or ("إيصال غير مطابق أو تم إلغاؤه من قبل المشرف." if ar else "Invalid receipt or rejected by admin.")
        receipt.rejection_reason = reason
        receipt.reviewed_by = request.user
        receipt.reviewed_at = timezone.now()
        receipt.save()

        receipt.booking.status = 'rejected'
        receipt.booking.save()

        msg = f"تم رفض إيصال الطالب {receipt.booking.full_name} وإلغاء الطلب: ({reason}) ❌" if ar else f"Receipt for {receipt.booking.full_name} rejected: ({reason}) ❌"
        messages.warning(request, msg)
        return redirect('admin:tours_depositreceipt_changelist')

    def approve_selected(self, request, queryset):
        ar = is_arabic()
        for r in queryset:
            r.status = 'approved'
            r.reviewed_by = request.user
            r.reviewed_at = timezone.now()
            r.save()
            r.booking.status = 'confirmed'
            r.booking.save()
        msg = f"تم اعتماد {queryset.count()} إيصال وتأكيد حجوزاتهم بنجاح." if ar else f"Approved {queryset.count()} receipts and confirmed bookings."
        messages.success(request, msg)
    approve_selected.short_description = _bi("اعتماد الإيصالات المحددة وتأكيد الحجز ✅", "Approve selected receipts & confirm tours ✅")

    def reject_selected(self, request, queryset):
        ar = is_arabic()
        for r in queryset:
            r.status = 'rejected'
            r.rejection_reason = "تم الرفض بواسطة المشرف." if ar else "Rejected by admin."
            r.reviewed_by = request.user
            r.reviewed_at = timezone.now()
            r.save()
            r.booking.status = 'rejected'
            r.booking.save()
        msg = f"تم رفض {queryset.count()} إيصال وإلغاء طلباتهم." if ar else f"Rejected {queryset.count()} receipts and cancelled bookings."
        messages.warning(request, msg)
    reject_selected.short_description = _bi("رفض الإيصالات المحددة وإلغاء الطلبات ❌", "Reject selected receipts & cancel tours ❌")


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
        (_bi('بيانات الطالب والتواصل', 'Student & Contact Details'), {
            'fields': (('full_name', 'user'), ('phone', 'email'), 'message')
        }),
        (_bi('تفاصيل المعاينة والسكن', 'Tour & Property Details'), {
            'fields': (('property', 'tour_date', 'tour_type'),)
        }),
        (_bi('حالة الحجز والعربون', 'Booking & Deposit Status'), {
            'fields': ('status', 'deposit_details_preview', 'created_at')
        }),
    )

    def student_contact(self, obj):
        ar = is_arabic()
        clean_phone = ''.join(c for c in (obj.phone or '') if c.isdigit())
        if clean_phone.startswith('0'):
            clean_phone = '2' + clean_phone
        wa_url = f"https://wa.me/{clean_phone}"
        btn_label = "💬 واتساب" if ar else "💬 WhatsApp"
        btn_title = "مراسلة الطالب على واتساب" if ar else "Message student on WhatsApp"
        return format_html(
            '<span style="display:inline-flex; align-items:center; gap:6px; white-space:nowrap !important;">'
            '<span>{}</span>'
            '<a href="{}" target="_blank" title="{}" style="display:inline-block; text-decoration:none; background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; padding:1px 6px; border-radius:4px; font-size:11px; font-weight:bold;">{}</a>'
            '</span>',
            obj.phone, wa_url, btn_title, btn_label
        )
    student_contact.short_description = _bi("الهاتف والتواصل", "Contact & WhatsApp")

    def property_title(self, obj):
        if obj.property:
            return obj.property.title_ar or obj.property.title
        return "-"
    property_title.short_description = _bi("السكن المطلوب", "Property")

    def tour_type_badge(self, obj):
        ar = is_arabic()
        if obj.tour_type == 'in_person':
            label = '🚶‍♂️ ميدانية' if ar else '🚶‍♂️ In-Person'
            return format_html(f'<span style="display:inline-block; white-space:nowrap !important; background:#f1f5f9; color:#334155; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:bold; border:1px solid #cbd5e1;">{label}</span>')
        label = '📹 فيديو' if ar else '📹 Video'
        return format_html(f'<span style="display:inline-block; white-space:nowrap !important; background:#ede9fe; color:#6d28d9; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:bold; border:1px solid #ddd6fe;">{label}</span>')
    tour_type_badge.short_description = _bi("النوع", "Tour Type")

    def deposit_status_badge(self, obj):
        ar = is_arabic()
        currency = "ج.م" if ar else "EGP"
        if hasattr(obj, 'deposit_receipt'):
            r = obj.deposit_receipt
            receipt_url = reverse('admin:tours_depositreceipt_change', args=[r.id])
            if r.status == 'approved':
                paid_lbl = f"مدفوع ({r.amount} {currency}) ✅" if ar else f"Paid ({r.amount} {currency}) ✅"
                return format_html(
                    '<a href="{}" style="display:inline-block; white-space:nowrap !important; background:#dcfce7; color:#15803d; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:bold; text-decoration:none; border:1px solid #bbf7d0;">'
                    '{}'
                    '</a>',
                    receipt_url, paid_lbl
                )
            elif r.status == 'rejected':
                rej_lbl = "عربون مرفوض ❌" if ar else "Deposit Rejected ❌"
                return format_html(
                    '<a href="{}" style="display:inline-block; white-space:nowrap !important; background:#fee2e2; color:#b91c1c; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:bold; text-decoration:none; border:1px solid #fecaca;">'
                    '{}'
                    '</a>',
                    receipt_url, rej_lbl
                )
            pend_lbl = f"قيد المراجعة ({r.amount} {currency}) ⏳" if ar else f"Pending Review ({r.amount} {currency}) ⏳"
            return format_html(
                '<a href="{}" style="display:inline-block; white-space:nowrap !important; background:#fef9c3; color:#854d0e; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:bold; text-decoration:none; border:1px solid #fef08a;">'
                '{}'
                '</a>',
                receipt_url, pend_lbl
            )
        no_rec = "بدون إيصال" if ar else "No Receipt"
        return format_html(f'<span style="color:#94a3b8; font-size:11px; white-space:nowrap !important;">{no_rec}</span>')
    deposit_status_badge.short_description = _bi("العربون والإيصال", "Deposit Status")

    def booking_status_badge(self, obj):
        ar = is_arabic()
        if obj.status == 'confirmed':
            label = 'مؤكد ✅' if ar else 'Confirmed ✅'
            return format_html(f'<span style="display:inline-block; white-space:nowrap !important; background:#dcfce7; color:#15803d; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #bbf7d0;">{label}</span>')
        elif obj.status == 'pending':
            label = 'قيد الانتظار ⏳' if ar else 'Pending ⏳'
            return format_html(f'<span style="display:inline-block; white-space:nowrap !important; background:#fef9c3; color:#854d0e; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #fef08a;">{label}</span>')
        elif obj.status == 'rejected':
            label = 'مرفوض ❌' if ar else 'Rejected ❌'
            return format_html(f'<span style="display:inline-block; white-space:nowrap !important; background:#fee2e2; color:#b91c1c; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #fecaca;">{label}</span>')
        elif obj.status == 'completed':
            label = 'مكتملة 🏁' if ar else 'Completed 🏁'
            return format_html(f'<span style="display:inline-block; white-space:nowrap !important; background:#f1f5f9; color:#475569; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #cbd5e1;">{label}</span>')
        elif obj.status == 'cancelled':
            label = 'ملغية 🚫' if ar else 'Cancelled 🚫'
            return format_html(f'<span style="display:inline-block; white-space:nowrap !important; background:#fee2e2; color:#b91c1c; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #fecaca;">{label}</span>')
        return obj.get_status_display()
    booking_status_badge.short_description = _bi("حالة المعاينة", "Tour Status")

    def created_at_short(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    created_at_short.short_description = _bi("تاريخ الطلب", "Request Date")

    def deposit_details_preview(self, obj):
        ar = is_arabic()
        if hasattr(obj, 'deposit_receipt'):
            r = obj.deposit_receipt
            receipt_url = reverse('admin:tours_depositreceipt_change', args=[r.id])
            img_html = f'<div style="margin-top:6px;"><a href="{r.receipt_image.url}" target="_blank"><img src="{r.receipt_image.url}" style="max-width:240px; border-radius:6px; border:1px solid #cbd5e1;" /></a></div>' if r.receipt_image else ''
            
            lbl_amount = "المبلغ:" if ar else "Amount:"
            lbl_status = "الحالة:" if ar else "Status:"
            lbl_sender = "اسم / رقم المحول:" if ar else "Sender Details:"
            lbl_ref = "الرقم المرجعي:" if ar else "Reference Number:"
            lbl_link = "انتقل لصفحة مراجعة هذا الإيصال ↗" if ar else "Open receipt review page ↗"
            curr = "ج.م" if ar else "EGP"

            return format_html(
                '<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px; font-size:12px; max-width:500px;">'
                '<div><strong>{}</strong> {} {} ({})</div>'
                '<div><strong>{}</strong> {}</div>'
                '<div><strong>{}</strong> {}</div>'
                '<div><strong>{}</strong> {}</div>'
                '<div><a href="{}" style="color:#0284c7; font-weight:bold;">{}</a></div>'
                '{}'
                '</div>',
                lbl_amount, r.amount, curr, r.get_payment_method_display(),
                lbl_status, r.get_status_display(),
                lbl_sender, r.sender_info or '-',
                lbl_ref, r.reference_number or '-',
                receipt_url, lbl_link,
                format_html(img_html)
            )
        return "لا يوجد إيصال عربون مرتبط بهذا الحجز." if ar else "No deposit receipt attached to this booking."
    deposit_details_preview.short_description = _bi("بيانات إيصال العربون المرفق", "Deposit Details")

    def confirm_selected_tours(self, request, queryset):
        ar = is_arabic()
        count = queryset.update(status='confirmed')
        msg = f"تم تأكيد {count} موعد معاينة بنجاح ✅" if ar else f"Confirmed {count} tour bookings successfully ✅"
        messages.success(request, msg)
    confirm_selected_tours.short_description = _bi("تأكيد مواعيد المعاينة المحددة ✅", "Confirm selected tour bookings ✅")

    def cancel_selected_tours(self, request, queryset):
        ar = is_arabic()
        count = queryset.update(status='cancelled')
        msg = f"تم إلغاء {count} موعد معاينة 🚫" if ar else f"Cancelled {count} tour bookings 🚫"
        messages.warning(request, msg)
    cancel_selected_tours.short_description = _bi("إلغاء مواعيد المعاينة المحددة 🚫", "Cancel selected tour bookings 🚫")
