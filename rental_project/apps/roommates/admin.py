from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
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
        ('بيانات الطالب والنوع', {
            'fields': (
                ('student_name', 'gender'),
                'user',
            )
        }),
        ('الارتباط الأكاديمي والدراسة', {
            'fields': (
                ('university', 'faculty', 'academic_year'),
            )
        }),
        ('مواصفات السكن والمنطقة والميزانية', {
            'fields': (
                ('target_area', 'budget_max_egp'),
                'move_in_date',
            )
        }),
        ('طبيعة المعيشة والنبذة الشخصية', {
            'fields': (
                ('sleep_habit', 'smoking'),
                'bio',
            )
        }),
        ('بيانات التواصل وحالة الإعلان', {
            'fields': (
                ('contact_phone', 'whatsapp_number'),
                ('is_active', 'created_at'),
            )
        }),
    )

    def student_info(self, obj):
        if obj.user:
            try:
                user_url = reverse('admin:auth_user_change', args=[obj.user.id])
                user_badge = format_html(
                    ' <a href="{}" style="color:#2563eb; text-decoration:none; font-weight:normal; font-size:11px;" title="عرض حساب المستخدم في لوحة التحكم">(@{})</a>',
                    user_url, obj.user.username
                )
            except Exception:
                user_badge = format_html(' <small style="color:#64748b;">(@{})</small>', obj.user.username)
        else:
            user_badge = format_html(' <span style="color:#94a3b8; font-size:10.5px; font-weight:normal;">(زائر)</span>')

        return format_html(
            '<span style="white-space:nowrap !important; font-weight:bold; color:#0f172a; font-size:12px;">{}{}</span>',
            obj.student_name, user_badge
        )
    student_info.short_description = "اسم الطالب والحساب"

    def gender_badge(self, obj):
        if obj.gender == 'female':
            return format_html(
                '<span style="display:inline-block; white-space:nowrap !important; background:#fdf2f8; color:#be185d; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #fbcfe8;">'
                'طالبة (بنات) 👩'
                '</span>'
            )
        return format_html(
            '<span style="display:inline-block; white-space:nowrap !important; background:#f0fdf4; color:#15803d; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #bbf7d0;">'
            'طالب (شباب) 👨'
            '</span>'
        )
    gender_badge.short_description = "النوع"

    def study_info(self, obj):
        uni = obj.university.short_code if obj.university else ''
        fac = obj.faculty or ''
        text = f"{uni} - {fac}" if uni and fac else (uni or fac or '-')
        return format_html('<span style="white-space:nowrap; font-size:11.5px; color:#334155;">{}</span>', text)
    study_info.short_description = "الجامعة والكلية"

    def budget_display(self, obj):
        val = f"{obj.budget_max_egp:,}" if obj.budget_max_egp else "0"
        return format_html(
            '<span style="display:inline-block; white-space:nowrap !important; font-weight:bold; color:#059669; font-size:11.5px;">'
            '{} ج.م / شهر'
            '</span>',
            val
        )
    budget_display.short_description = "الميزانية"

    def smoking_badge(self, obj):
        if obj.smoking:
            return format_html(
                '<span style="display:inline-block; white-space:nowrap !important; background:#fef2f2; color:#b91c1c; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:10.5px; border:1px solid #fecaca;">'
                'مدخن 🚬'
                '</span>'
            )
        return format_html(
            '<span style="display:inline-block; white-space:nowrap !important; background:#f0fdf4; color:#15803d; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:10.5px; border:1px solid #bbf7d0;">'
            'غير مدخن 🚭'
            '</span>'
        )
    smoking_badge.short_description = "التدخين"

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
    bio_snippet.short_description = "مواصفات السكن المطلوبة"

    def contact_with_whatsapp(self, obj):
        phone = obj.contact_phone or obj.whatsapp_number
        if not phone:
            return format_html('<span style="color:#94a3b8; font-size:11px;">-</span>')
        wa_url = obj.get_whatsapp_url()
        return format_html(
            '<span style="display:inline-flex; align-items:center; gap:5px; white-space:nowrap !important;">'
            '<span>{}</span>'
            '<a href="{}" target="_blank" title="مراسلة على واتساب" style="display:inline-block; text-decoration:none; background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; padding:1px 5px; border-radius:4px; font-size:10.5px; font-weight:bold;">💬 واتساب</a>'
            '</span>',
            phone, wa_url
        )
    contact_with_whatsapp.short_description = "التواصل والواتساب"

    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="display:inline-block; white-space:nowrap !important; background:#dcfce7; color:#15803d; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #bbf7d0;">'
                'نشط متاح 🟢'
                '</span>'
            )
        return format_html(
            '<span style="display:inline-block; white-space:nowrap !important; background:#f1f5f9; color:#64748b; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #e2e8f0;">'
            'غير نشط / مكتمل ⚪'
            '</span>'
        )
    status_badge.short_description = "حالة الإعلان"

    def created_at_short(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")
    created_at_short.short_description = "تاريخ النشر"

    def make_active(self, request, queryset):
        count = queryset.update(is_active=True)
        messages.success(request, f"تم تنشيط {count} إعلان بنجاح 🟢")
    make_active.short_description = "تنشيط الإعلانات المحددة 🟢"

    def make_inactive(self, request, queryset):
        count = queryset.update(is_active=False)
        messages.warning(request, f"تم إيقاف {count} إعلان (أكتمل السكن) ⚪")
    make_inactive.short_description = "إيقاف الإعلانات المحددة (أكتمل السكن) ⚪"
