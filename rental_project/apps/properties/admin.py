from django.contrib.gis import admin as gis_admin
from django.contrib.gis.forms.widgets import OSMWidget
from django.utils.html import format_html
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
        'title_ar',
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
        ('سكن الطلاب والبيانات الأساسية', {
            'fields': (
                ('title', 'title_ar'),
                ('gender_policy', 'rental_type'),
                ('price_egp', 'deposit_egp', 'bills_included'),
                ('total_capacity', 'available_beds'),
                ('description', 'description_ar'),
                ('featured', 'badge', 'posted_days_ago'),
            )
        }),
        ('الارتباط بالجامعة والمترو وخريطة القاهرة (PostGIS)', {
            'description': 'حدد موقع السكن على خريطة القاهرة لربطه بدقة بالجامعة ومحطة المترو.',
            'fields': (
                ('university', 'distance_to_university_km', 'walking_minutes'),
                'nearest_metro',
                'location',
                ('address', 'city'),
                ('state', 'zip_code', 'country'),
                ('lat', 'lng'),
            )
        }),
        ('المواصفات والخدمات الطلابية', {
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
        ('بيانات التواصل والتأجير', {
            'fields': (
                ('agent_name', 'phone_number'),
                ('whatsapp_number', 'agent_email'),
                'agent_avatar',
            )
        }),
        ('معلومات تقنية قديمة / إضافية', {
            'fields': (('price', 'buy_price', 'rental_period', 'property_type'), 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def thumbnail_preview(self, obj):
        if obj.primary_image:
            return format_html('<img src="{}" style="width: 54px; height: 38px; object-fit: cover; border-radius: 6px;" />', obj.primary_image)
        return "-"
    thumbnail_preview.short_description = "صورة"

    def thumbnail_large(self, obj):
        if obj.primary_image:
            return format_html('<img src="{}" style="max-width: 320px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);" />', obj.primary_image)
        return "-"
    thumbnail_large.short_description = "معاينة الصورة"

    def price_egp_display(self, obj):
        return f"{obj.price_egp:,} ج.م / شهر"
    price_egp_display.short_description = "الإيجار"

    def gender_badge(self, obj):
        if obj.gender_policy == 'female_only':
            return format_html('<span style="background:#fce7f3; color:#be185d; padding:3px 8px; border-radius:12px; font-weight:bold; font-size:11px;">طالبات (بنات)</span>')
        elif obj.gender_policy == 'male_only':
            return format_html('<span style="background:#dbeafe; color:#1d4ed8; padding:3px 8px; border-radius:12px; font-weight:bold; font-size:11px;">طلاب (شباب)</span>')
        return format_html('<span style="background:#f1f5f9; color:#475569; padding:3px 8px; border-radius:12px; font-weight:bold; font-size:11px;">للجميع</span>')
    gender_badge.short_description = "نوع السكن"

    def rental_type_display(self, obj):
        return obj.get_rental_type_display_ar()
    rental_type_display.short_description = "نوع الإيجار"

    def beds_status(self, obj):
        return f"{obj.available_beds} من أصل {obj.total_capacity} سرير"
    beds_status.short_description = "الأسِرّة المتاحة"
