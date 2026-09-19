from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from apps.core.i18n import _bi, is_arabic
from .models import RoommatePost

@admin.register(RoommatePost)
class RoommatePostAdmin(admin.ModelAdmin):
    list_display = (
        'student_info',
        'gender_badge',
        'study_info',
        'target_area',
        'budget_display',
        'smoking_badge',
        'bio_snippet',
        'contact_with_whatsapp',
        'status_badge',
        'created_at_short',
    )
    list_filter = ('gender', 'is_active', 'smoking', 'university', 'created_at')
    search_fields = ('student_name', 'faculty', 'target_area', 'contact_phone', 'whatsapp_number', 'bio')
    readonly_fields = ('created_at',)
    actions = ['make_active', 'make_inactive']

    fieldsets = (
        (_bi('بيانات الطالب والنوع', 'Student & Gender Information'), {
            'fields': (
                ('student_name', 'gender'),
                'user',
            )
        }),
        (_bi('الارتباط الأكاديمي والدراسة', 'Academic & University Details'), {
            'fields': (
                ('university', 'faculty', 'academic_year'),
            )
        }),
        (_bi('مواصفات السكن والمنطقة والميزانية', 'Housing Area & Budget Preferences'), {
            'fields': (
                ('target_area', 'budget_max_egp'),
                'move_in_date',
            )
        }),
        (_bi('طبيعة المعيشة والنبذة الشخصية', 'Living Habits & Personal Bio'), {
            'fields': (
                ('sleep_habit', 'smoking'),
                'bio',
            )
        }),
        (_bi('بيانات التواصل وحالة الإعلان', 'Contact Details & Listing Status'), {
            'fields': (
                ('contact_phone', 'whatsapp_number'),
                ('is_active', 'created_at'),
            )
        }),
    )

    def student_info(self, obj):
        ar = is_arabic()
        if obj.user:
            try:
                user_url = reverse('admin:auth_user_change', args=[obj.user.id])
                tooltip = "عرض حساب المستخدم في لوحة التحكم" if ar else "View user account in admin panel"
                user_badge = format_html(
                    ' <a href="{}" style="color:#2563eb; text-decoration:none; font-weight:normal; font-size:11px;" title="{}">(@{})</a>',
                    user_url, tooltip, obj.user.username
                )
            except Exception:
                user_badge = format_html(' <small style="color:#64748b;">(@{})</small>', obj.user.username)
        else:
            visitor_label = "(زائر)" if ar else "(Visitor)"
            user_badge = format_html(' <span style="color:#94a3b8; font-size:10.5px; font-weight:normal;">{}</span>', visitor_label)

        return format_html(
            '<span style="white-space:nowrap !important; font-weight:bold; color:#0f172a; font-size:12px;">{}{}</span>',
            obj.student_name, user_badge
        )
    student_info.short_description = _bi("اسم الطالب والحساب", "Student & Account")

    def gender_badge(self, obj):
        ar = is_arabic()
        if obj.gender == 'female':
            label = 'طالبة (بنات) 👩' if ar else 'Female Student 👩'
            return format_html(
                '<span style="display:inline-block; white-space:nowrap !important; background:#fdf2f8; color:#be185d; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #fbcfe8;">'
                '{}'
                '</span>',
                label
            )
        label = 'طالب (شباب) 👨' if ar else 'Male Student 👨'
        return format_html(
            '<span style="display:inline-block; white-space:nowrap !important; background:#f0fdf4; color:#15803d; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #bbf7d0;">'
            '{}'
            '</span>',
            label
        )
    gender_badge.short_description = _bi("النوع", "Gender")

    def study_info(self, obj):
        uni = obj.university.short_code if obj.university else ''
        fac = obj.faculty or ''
        text = f"{uni} - {fac}" if uni and fac else (uni or fac or '-')
        return format_html('<span style="white-space:nowrap; font-size:11.5px; color:#334155;">{}</span>', text)
    study_info.short_description = _bi("الجامعة والكلية", "University & Faculty")

    def budget_display(self, obj):
        ar = is_arabic()
        val = f"{obj.budget_max_egp:,}" if obj.budget_max_egp else "0"
        currency = "ج.م / شهر" if ar else "EGP / mo"
        return format_html(
            '<span style="display:inline-block; white-space:nowrap !important; font-weight:bold; color:#059669; font-size:11.5px;">'
            '{} {}'
            '</span>',
            val, currency
        )
    budget_display.short_description = _bi("الميزانية", "Budget")

    def smoking_badge(self, obj):
        ar = is_arabic()
        if obj.smoking:
            label = 'مدخن 🚬' if ar else 'Smoker 🚬'
            return format_html(
                '<span style="display:inline-block; white-space:nowrap !important; background:#fef2f2; color:#b91c1c; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:10.5px; border:1px solid #fecaca;">'
                '{}'
                '</span>',
                label
            )
        label = 'غير مدخن 🚭' if ar else 'Non-smoker 🚭'
        return format_html(
            '<span style="display:inline-block; white-space:nowrap !important; background:#f0fdf4; color:#15803d; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:10.5px; border:1px solid #bbf7d0;">'
            '{}'
            '</span>',
            label
        )
    smoking_badge.short_description = _bi("التدخين", "Smoking")

    def bio_snippet(self, obj):
        if not obj.bio:
            return format_html('<span style="color:#94a3b8; font-size:11px;">-</span>')
        full_text = obj.bio.strip()
        short_text = full_text[:45] + ("..." if len(full_text) > 45 else "")
        return format_html(
            '<span style="display:inline-block; max-width:180px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-size:11px; color:#475569; vertical-align:middle;" title="{}">'
            '{}'
            '</span>',
            full_text, short_text
        )
    bio_snippet.short_description = _bi("مواصفات السكن المطلوبة", "Housing Bio / Specs")

    def contact_with_whatsapp(self, obj):
        ar = is_arabic()
        phone = obj.contact_phone or obj.whatsapp_number
        if not phone:
            return format_html('<span style="color:#94a3b8; font-size:11px;">-</span>')
        wa_url = obj.get_whatsapp_url()
        btn_label = "💬 واتساب" if ar else "💬 WhatsApp"
        btn_title = "مراسلة على واتساب" if ar else "Message on WhatsApp"
        return format_html(
            '<span style="display:inline-flex; align-items:center; gap:5px; white-space:nowrap !important;">'
            '<span>{}</span>'
            '<a href="{}" target="_blank" title="{}" style="display:inline-block; text-decoration:none; background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; padding:1px 5px; border-radius:4px; font-size:10.5px; font-weight:bold;">{}</a>'
            '</span>',
            phone, wa_url, btn_title, btn_label
        )
    contact_with_whatsapp.short_description = _bi("التواصل والواتساب", "Contact & WhatsApp")

    def status_badge(self, obj):
        ar = is_arabic()
        if obj.is_active:
            label = 'نشط متاح 🟢' if ar else 'Active 🟢'
            return format_html(
                '<span style="display:inline-block; white-space:nowrap !important; background:#dcfce7; color:#15803d; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #bbf7d0;">'
                '{}'
                '</span>',
                label
            )
        label = 'غير نشط / مكتمل ⚪' if ar else 'Inactive / Filled ⚪'
        return format_html(
            '<span style="display:inline-block; white-space:nowrap !important; background:#f1f5f9; color:#64748b; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #e2e8f0;">'
            '{}'
            '</span>',
            label
        )
    status_badge.short_description = _bi("حالة الإعلان", "Status")

    def created_at_short(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")
    created_at_short.short_description = _bi("تاريخ النشر", "Created Date")

    def make_active(self, request, queryset):
        ar = is_arabic()
        count = queryset.update(is_active=True)
        msg = f"تم تنشيط {count} إعلان بنجاح 🟢" if ar else f"Successfully activated {count} listings 🟢"
        messages.success(request, msg)
    make_active.short_description = _bi("تنشيط الإعلانات المحددة 🟢", "Activate selected listings 🟢")

    def make_inactive(self, request, queryset):
        ar = is_arabic()
        count = queryset.update(is_active=False)
        msg = f"تم إيقاف {count} إعلان (أكتمل السكن) ⚪" if ar else f"Deactivated {count} listings (Filled) ⚪"
        messages.warning(request, msg)
    make_inactive.short_description = _bi("إيقاف الإعلانات المحددة (أكتمل السكن) ⚪", "Deactivate selected listings (Filled) ⚪")
