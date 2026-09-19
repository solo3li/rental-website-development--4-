from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from apps.core.i18n import _bi, is_arabic
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
        (_bi('بيانات الحساب الأساسية والنوع', 'Account Basics & Type'), {
            'fields': (
                ('user', 'user_type', 'is_verified'),
                ('gender', 'avatar', 'avatar_preview'),
            )
        }),
        (_bi('معلومات التواصل المباشر', 'Contact Details'), {
            'fields': (
                ('phone', 'whatsapp'),
            )
        }),
        (_bi('بيانات الطالب الأكاديمية (خاص بالطلاب)', 'Academic Details (Students)'), {
            'fields': (
                ('university', 'faculty', 'academic_year'),
            )
        }),
        (_bi('بيانات السكن والمكتب (خاص بالملاك والمؤجرين)', 'Property & Office Info (Landlords)'), {
            'fields': (
                'company_name',
                'bio',
            )
        }),
        (_bi('تاريخ التسجيل', 'Registration Date'), {
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
    avatar_preview.short_description = _bi("الصورة", "Avatar")

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
    user_name_and_email.short_description = _bi("المستخدم والبريد", "User & Email")

    def user_type_badge(self, obj):
        ar = is_arabic()
        if obj.is_student:
            label = 'طالب 🎓' if ar else 'Student 🎓'
            return format_html(
                '<span style="display:inline-block; white-space:nowrap !important; background:#eff6ff; color:#1d4ed8; padding:2px 7px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #bfdbfe;">'
                '{}'
                '</span>',
                label
            )
        label = 'صاحب سكن 🏢' if ar else 'Landlord 🏢'
        return format_html(
            '<span style="display:inline-block; white-space:nowrap !important; background:#f5f3ff; color:#7c3aed; padding:2px 7px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #ddd6fe;">'
            '{}'
            '</span>',
            label
        )
    user_type_badge.short_description = _bi("نوع الحساب", "Account Type")

    def gender_badge(self, obj):
        ar = is_arabic()
        if obj.gender == 'female':
            label = 'طالبة 👩' if ar else 'Female 👩'
            return format_html(
                '<span style="display:inline-block; white-space:nowrap !important; background:#fdf2f8; color:#be185d; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #fbcfe8;">'
                '{}'
                '</span>',
                label
            )
        label = 'طالب 👨' if ar else 'Male 👨'
        return format_html(
            '<span style="display:inline-block; white-space:nowrap !important; background:#f0fdf4; color:#15803d; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #bbf7d0;">'
            '{}'
            '</span>',
            label
        )
    gender_badge.short_description = _bi("النوع", "Gender")

    def contact_with_whatsapp(self, obj):
        ar = is_arabic()
        phone = obj.phone or obj.whatsapp
        if not phone:
            return format_html('<span style="color:#94a3b8; font-size:11px;">-</span>')
        clean_phone = ''.join(c for c in phone if c.isdigit())
        if clean_phone.startswith('0'):
            clean_phone = '2' + clean_phone
        wa_url = f"https://wa.me/{clean_phone}"
        btn_label = "💬 واتساب" if ar else "💬 WhatsApp"
        btn_title = "مراسلة على واتساب" if ar else "Message on WhatsApp"
        return format_html(
            '<span style="display:inline-flex; align-items:center; gap:5px; white-space:nowrap !important;">'
            '<span>{}</span>'
            '<a href="{}" target="_blank" title="{}" style="display:inline-block; text-decoration:none; background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; padding:1px 5px; border-radius:4px; font-size:10.5px; font-weight:bold;">{}</a>'
            '</span>',
            phone, wa_url, btn_title, btn_label
        )
    contact_with_whatsapp.short_description = _bi("الهاتف والتواصل", "Contact & WhatsApp")

    def university_or_company(self, obj):
        ar = is_arabic()
        if obj.is_student:
            uni_name = obj.university.short_code if obj.university else ''
            faculty = obj.faculty or ''
            text = f"{uni_name} - {faculty}" if uni_name and faculty else (uni_name or faculty or '-')
            return format_html('<span style="white-space:nowrap; font-size:11.5px; color:#334155;">{}</span>', text)
        owner_fallback = 'مالك فردي' if ar else 'Individual Landlord'
        return format_html('<span style="white-space:nowrap; font-size:11.5px; color:#334155;">{}</span>', obj.company_name or owner_fallback)
    university_or_company.short_description = _bi("الجامعة / الجهة", "University / Organization")

    def verification_badge(self, obj):
        ar = is_arabic()
        if obj.is_verified:
            label = 'موثق ✅' if ar else 'Verified ✅'
            return format_html(
                '<span style="display:inline-block; white-space:nowrap !important; background:#dcfce7; color:#15803d; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #bbf7d0;">'
                '{}'
                '</span>',
                label
            )
        label = 'قيد التحقق ⚠️' if ar else 'Pending Verification ⚠️'
        return format_html(
            '<span style="display:inline-block; white-space:nowrap !important; background:#fef3c7; color:#b45309; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px; border:1px solid #fde68a;">'
            '{}'
            '</span>',
            label
        )
    verification_badge.short_description = _bi("التوثيق", "Verification")

    def activity_summary(self, obj):
        ar = is_arabic()
        try:
            if obj.is_landlord:
                props_count = obj.user.owned_properties.count()
                unit_label = 'عقار' if ar else 'Properties'
                return format_html(
                    '<span style="display:inline-block; white-space:nowrap; font-size:11px; color:#475569;">'
                    '🏢 <strong>{}</strong> {}'
                    '</span>',
                    props_count, unit_label
                )
            else:
                tours_count = obj.user.tour_bookings.count()
                roommates_count = obj.user.roommate_posts.count()
                if ar:
                    summary_text = f"📅 <strong>{tours_count}</strong> معاينة • 👥 <strong>{roommates_count}</strong> رفيق"
                else:
                    summary_text = f"📅 <strong>{tours_count}</strong> Tours • 👥 <strong>{roommates_count}</strong> Roommates"
                return format_html(
                    '<span style="display:inline-block; white-space:nowrap; font-size:11px; color:#475569;">'
                    '{}'
                    '</span>',
                    format_html(summary_text)
                )
        except Exception:
            return "-"
    activity_summary.short_description = _bi("النشاط", "Activity")

    def created_at_short(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")
    created_at_short.short_description = _bi("تاريخ الانضمام", "Joined Date")

    def verify_selected_profiles(self, request, queryset):
        ar = is_arabic()
        count = queryset.update(is_verified=True)
        msg = f"تم توثيق {count} حساب بنجاح ✅" if ar else f"Successfully verified {count} accounts ✅"
        messages.success(request, msg)
    verify_selected_profiles.short_description = _bi("توثيق الحسابات المحددة ✅", "Verify selected profiles ✅")

    def unverify_selected_profiles(self, request, queryset):
        ar = is_arabic()
        count = queryset.update(is_verified=False)
        msg = f"تم إلغاء توثيق {count} حساب ⚠️" if ar else f"Unverified {count} accounts ⚠️"
        messages.warning(request, msg)
    unverify_selected_profiles.short_description = _bi("إلغاء توثيق الحسابات المحددة ⚠️", "Unverify selected profiles ⚠️")
