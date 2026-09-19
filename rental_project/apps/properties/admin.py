from django.contrib.gis import admin as gis_admin
from django.contrib.gis.forms.widgets import OSMWidget
from django.utils.html import format_html
from apps.core.i18n import _bi, is_arabic
from .models import Property, University, MetroStation

class CustomOSMWidget(OSMWidget):
    template_name = 'gis/openlayers-osm.html'
    default_zoom = 12
    default_lat = 30.0444
    default_lon = 31.2357

@gis_admin.register(University)
class UniversityAdmin(gis_admin.GISModelAdmin):
    gis_widget = CustomOSMWidget
    gis_widget_kwargs = {
        'attrs': {
            'default_zoom': 13,
            'default_lat': 30.0276,
            'default_lon': 31.2089,
        }
    }
    list_display = ('name_ar', 'name', 'short_code', 'city', 'nearest_metro')
    search_fields = ('name', 'name_ar', 'short_code', 'city')


@gis_admin.register(MetroStation)
class MetroStationAdmin(gis_admin.GISModelAdmin):
    gis_widget = CustomOSMWidget
    gis_widget_kwargs = {
        'attrs': {
            'default_zoom': 13,
            'default_lat': 30.0444,
            'default_lon': 31.2357,
        }
    }
    list_display = ('name_ar', 'name', 'line')
    list_filter = ('line',)
    search_fields = ('name', 'name_ar')


@gis_admin.register(Property)
class PropertyAdmin(gis_admin.GISModelAdmin):
    gis_widget = CustomOSMWidget
    gis_widget_kwargs = {
        'attrs': {
            'default_zoom': 13,
            'default_lat': 30.0382,
            'default_lon': 31.2119,
        }
    }
    
    list_display = (
        'thumbnail_preview',
        'title_display',
        'gender_badge',
        'rental_type_display',
        'price_egp_display',
        'beds_status',
        'university',
        'city',
        'featured',
    )
    list_filter = ('gender_policy', 'rental_type', 'university', 'bills_included', 'featured', 'city')
    search_fields = ('title', 'title_ar', 'address', 'city', 'description', 'description_ar')
    readonly_fields = ('created_at', 'thumbnail_large')

    fieldsets = (
        (_bi('سكن الطلاب والبيانات الأساسية', 'Student Housing & Basic Details'), {
            'fields': (
                ('title', 'title_ar'),
                ('gender_policy', 'rental_type'),
                ('price_egp', 'deposit_egp', 'bills_included'),
                ('total_capacity', 'available_beds'),
                ('description', 'description_ar'),
                ('featured', 'badge', 'posted_days_ago'),
            )
        }),
        (_bi('الارتباط بالجامعة والمترو وخريطة القاهرة (PostGIS)', 'University, Metro & Cairo Map (PostGIS)'), {
            'description': _bi(
                'حدد موقع السكن على خريطة القاهرة لربطه بدقة بالجامعة ومحطة المترو.',
                'Pin the housing location on the Cairo map to link with university and metro stations.'
            ),
            'fields': (
                ('university', 'distance_to_university_km', 'walking_minutes'),
                'nearest_metro',
                'location',
                ('address', 'city'),
                ('state', 'zip_code', 'country'),
                ('lat', 'lng'),
            )
        }),
        (_bi('المواصفات والخدمات الطلابية', 'Student Specs & Amenities'), {
            'fields': (
                ('bedrooms', 'bathrooms', 'area_sqft'),
                ('floor_number', 'has_elevator'),
                ('study_desk', 'wifi_speed'),
                ('curfew_time', 'is_supervised'),
                'amenities',
                'images',
                'thumbnail_large',
            )
        }),
        (_bi('بيانات التواصل والتأجير', 'Contact & Leasing Details'), {
            'fields': (
                ('agent_name', 'agent_phone'),
                ('whatsapp_number', 'agent_email'),
                'agent_avatar',
            )
        }),
        (_bi('معلومات تقنية قديمة / إضافية', 'Legacy / Additional Specs'), {
            'fields': (('price', 'buy_price', 'rental_period', 'property_type'), 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def title_display(self, obj):
        ar = is_arabic()
        return obj.title_ar or obj.title if ar else obj.title or obj.title_ar
    title_display.short_description = _bi("عنوان السكن", "Housing Title")

    def thumbnail_preview(self, obj):
        if obj.primary_image:
            return format_html('<img src="{}" style="width: 54px; height: 38px; object-fit: cover; border-radius: 6px;" />', obj.primary_image)
        return "-"
    thumbnail_preview.short_description = _bi("صورة", "Image")

    def thumbnail_large(self, obj):
        if obj.primary_image:
            return format_html('<img src="{}" style="max-width: 320px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);" />', obj.primary_image)
        return "-"
    thumbnail_large.short_description = _bi("معاينة الصورة", "Image Preview")

    def price_egp_display(self, obj):
        ar = is_arabic()
        curr = "ج.م / شهر" if ar else "EGP / mo"
        return f"{obj.price_egp:,} {curr}"
    price_egp_display.short_description = _bi("الإيجار", "Rent Price")

    def gender_badge(self, obj):
        ar = is_arabic()
        if obj.gender_policy == 'female_only':
            lbl = 'طالبات (بنات)' if ar else 'Female Students'
            return format_html(f'<span style="background:#fce7f3; color:#be185d; padding:3px 8px; border-radius:12px; font-weight:bold; font-size:11px; white-space:nowrap !important;">{lbl}</span>')
        elif obj.gender_policy == 'male_only':
            lbl = 'طلاب (شباب)' if ar else 'Male Students'
            return format_html(f'<span style="background:#dbeafe; color:#1d4ed8; padding:3px 8px; border-radius:12px; font-weight:bold; font-size:11px; white-space:nowrap !important;">{lbl}</span>')
        lbl = 'للجميع' if ar else 'All Students'
        return format_html(f'<span style="background:#f1f5f9; color:#475569; padding:3px 8px; border-radius:12px; font-weight:bold; font-size:11px; white-space:nowrap !important;">{lbl}</span>')
    gender_badge.short_description = _bi("نوع السكن", "Gender Policy")

    def rental_type_display(self, obj):
        ar = is_arabic()
        return obj.get_rental_type_display_ar() if ar else obj.get_rental_type_display()
    rental_type_display.short_description = _bi("نوع الإيجار", "Rental Type")

    def beds_status(self, obj):
        ar = is_arabic()
        if obj.available_beds == 0:
            lbl = f"مكتمل (0/{obj.total_capacity} سرير)" if ar else f"Full (0/{obj.total_capacity} Beds)"
            return format_html(f'<span style="display:inline-block; white-space:nowrap !important; background:#fee2e2; color:#b91c1c; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px;">{lbl}</span>')
        elif obj.available_beds <= 2:
            lbl = f"شاغر محدود ({obj.available_beds}/{obj.total_capacity} سرير)" if ar else f"Limited ({obj.available_beds}/{obj.total_capacity} Beds)"
            return format_html(f'<span style="display:inline-block; white-space:nowrap !important; background:#fef3c7; color:#b45309; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px;">{lbl}</span>')
        lbl = f"متاح ({obj.available_beds}/{obj.total_capacity} سرير)" if ar else f"Available ({obj.available_beds}/{obj.total_capacity} Beds)"
        return format_html(f'<span style="display:inline-block; white-space:nowrap !important; background:#dcfce7; color:#15803d; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px;">{lbl}</span>')
    beds_status.short_description = _bi("الأسِرّة الشاغرة", "Available Beds")
