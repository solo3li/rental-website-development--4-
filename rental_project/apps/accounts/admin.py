from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'avatar_preview',
        'user_name_and_email',
        'user_type_badge',
        'gender_badge',
        'contact_with_whatsapp',
        'university_or_company',
        'verification_badge',
        'activity_summary',
        'created_at_short',
    )
    list_filter = ('user_type', 'gender', 'is_verified', 'university', 'created_at')
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
        'phone',
        'whatsapp',
        'company_name',
        'faculty',
    )
    readonly_fields = ('created_at', 'avatar_preview')
    actions = ['verify_selected_profiles', 'unverify_selected_profiles']

    fieldsets = (
        ('بيانات الحساب الأساسية والنوع', {
            'fields': (
                ('user', 'user_type', 'is_verified'),
                ('gender', 'avatar', 'avatar_preview'),
            )
        }),
        ('معلومات التواصل المباشر', {
            'fields': (
                ('phone', 'whatsapp'),
            )
        }),
        ('بيانات الطالب الأكاديمية (خاص بالطلاب)', {
            'fields': (
                ('university', 'faculty', 'academic_year'),
            )
        }),
        ('بيانات السكن والمكتب (خاص بالملاك والمؤجرين)', {
            'fields': (
                'company_name',
                'bio',
            )
        }),
        ('تاريخ التسجيل', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def avatar_preview(self, obj):
        img_url = obj.avatar or 'https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=80&w=80'
        return format_html(
            '<img src="{}" style="width:34px; height:34px; border-radius:50%; object-fit:cover; border:1px solid #cbd5e1; display:block;" />',
            img_url
        )
    avatar_preview.short_description = "الصورة"

    def user_name_and_email(self, obj):
        full_name = obj.user.get_full_name() or obj.user.username
        email = obj.user.email or '-'
        return format_html(
            '<div style="white-space:nowrap;">'
            '<strong style="color:#0f172a; font-size:12px;">{}</strong>'
            '<div style="font-size:11px; color:#64748b;">{}</div>'
            '</div>',
            full_name, email
        )
    user_name_and_email.short_description = "المستخدم والبريد"

    def user_type_badge(self, obj):
        if obj.is_student:
            return format_html(
                '<span style="display:inline-block; white-space:nowrap; background:#eff6ff; color:#1d4ed8; padding:2px 7px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #bfdbfe;">'
                'طالب 🎓'
                '</span>'
            )
        return format_html(
            '<span style="display:inline-block; white-space:nowrap; background:#f5f3ff; color:#7c3aed; padding:2px 7px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #ddd6fe;">'
            'صاحب سكن 🏢'
            '</span>'
        )
    user_type_badge.short_description = "نوع الحساب"

    def gender_badge(self, obj):
        if obj.gender == 'female':
            return format_html(
                '<span style="display:inline-block; white-space:nowrap; background:#fdf2f8; color:#be185d; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #fbcfe8;">'
                'طالبة 👩'
                '</span>'
            )
        return format_html(
            '<span style="display:inline-block; white-space:nowrap; background:#f0fdf4; color:#15803d; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #bbf7d0;">'
            'طالب 👨'
            '</span>'
        )
    gender_badge.short_description = "النوع"

    def contact_with_whatsapp(self, obj):
        phone = obj.phone or obj.whatsapp
        if not phone:
            return format_html('<span style="color:#94a3b8; font-size:11px;">-</span>')
        clean_phone = ''.join(c for c in phone if c.isdigit())
        if clean_phone.startswith('0'):
            clean_phone = '2' + clean_phone
        wa_url = f"https://wa.me/{clean_phone}"
        return format_html(
            '<span style="display:inline-flex; align-items:center; gap:5px; white-space:nowrap;">'
            '<span>{}</span>'
            '<a href="{}" target="_blank" title="مراسلة على واتساب" style="display:inline-block; text-decoration:none; background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; padding:1px 5px; border-radius:4px; font-size:10.5px; font-weight:bold;">💬 واتساب</a>'
            '</span>',
            phone, wa_url
        )
    contact_with_whatsapp.short_description = "الهاتف والتواصل"

    def university_or_company(self, obj):
        if obj.is_student:
            uni_name = obj.university.short_code if obj.university else ''
            faculty = obj.faculty or ''
            text = f"{uni_name} - {faculty}" if uni_name and faculty else (uni_name or faculty or '-')
            return format_html('<span style="white-space:nowrap; font-size:11.5px; color:#334155;">{}</span>', text)
        return format_html('<span style="white-space:nowrap; font-size:11.5px; color:#334155;">{}</span>', obj.company_name or 'مالك فردي')
    university_or_company.short_description = "الجامعة / الجهة"

    def verification_badge(self, obj):
        if obj.is_verified:
            return format_html(
                '<span style="display:inline-block; white-space:nowrap; background:#dcfce7; color:#15803d; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #bbf7d0;">'
                'موثق ✅'
                '</span>'
            )
        return format_html(
            '<span style="display:inline-block; white-space:nowrap; background:#fef3c7; color:#b45309; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #fde68a;">'
            'قيد التحقق ⚠️'
            '</span>'
        )
    verification_badge.short_description = "التوثيق"

    def activity_summary(self, obj):
        try:
            if obj.is_landlord:
                props_count = obj.user.owned_properties.count()
                return format_html(
                    '<span style="display:inline-block; white-space:nowrap; font-size:11px; color:#475569;">'
                    '🏢 <strong>{}</strong> عقار'
                    '</span>',
                    props_count
                )
            else:
                tours_count = obj.user.tour_bookings.count()
                roommates_count = obj.user.roommate_posts.count()
                return format_html(
                    '<span style="display:inline-block; white-space:nowrap; font-size:11px; color:#475569;">'
                    '📅 <strong>{}</strong> معاينة • 👥 <strong>{}</strong> رفيق'
                    '</span>',
                    tours_count, roommates_count
                )
        except Exception:
            return "-"
    activity_summary.short_description = "النشاط"

    def created_at_short(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")
    created_at_short.short_description = "تاريخ الانضمام"

    def verify_selected_profiles(self, request, queryset):
        count = queryset.update(is_verified=True)
        messages.success(request, f"تم توثيق {count} حساب بنجاح ✅")
    verify_selected_profiles.short_description = "توثيق الحسابات المحددة ✅"

    def unverify_selected_profiles(self, request, queryset):
        count = queryset.update(is_verified=False)
        messages.warning(request, f"تم إلغاء توثيق {count} حساب ⚠️")
    unverify_selected_profiles.short_description = "إلغاء توثيق الحسابات المحددة ⚠️"
