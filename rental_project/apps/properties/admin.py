from django.contrib.gis import admin as gis_admin
from django.contrib.gis.forms.widgets import OSMWidget
from django.utils.html import format_html
from .models import Property

class CustomOSMWidget(OSMWidget):
    template_name = 'gis/openlayers-osm.html'
    default_zoom = 11
    default_lat = 40.7128
    default_lon = -74.0060

@gis_admin.register(Property)
class PropertyAdmin(gis_admin.GISModelAdmin):
    # Enables interactive map widget with CARTO Voyager tiles for selecting/editing location
    gis_widget = CustomOSMWidget
    gis_widget_kwargs = {
        'attrs': {
            'default_zoom': 11,
            'default_lat': 40.7128,
            'default_lon': -74.0060,
        }
    }
    
    list_display = (
        'thumbnail_preview',
        'title',
        'property_type',
        'listing_type',
        'price_display',
        'city',
        'bedrooms',
        'bathrooms',
        'featured',
        'is_family_friendly',
    )
    list_filter = ('property_type', 'listing_type', 'featured', 'is_family_friendly', 'city', 'state')
    search_fields = ('title', 'title_ar', 'address', 'city', 'description')
    readonly_fields = ('created_at', 'thumbnail_large')

    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('title', 'title_ar'),
                ('property_type', 'listing_type'),
                ('price', 'buy_price', 'rental_period'),
                ('description', 'description_ar'),
                ('featured', 'badge', 'posted_days_ago'),
            )
        }),
        ('Location & PostGIS Map', {
            'description': 'Click directly on the map below or drag the pin to set the exact property coordinates.',
            'fields': (
                'location',
                ('address', 'city'),
                ('state', 'zip_code', 'country'),
                ('lat', 'lng'),
            )
        }),
        ('Specifications & Amenities', {
            'fields': (
                ('bedrooms', 'bathrooms', 'area_sqft'),
                'is_family_friendly',
                'amenities',
                'family_highlights',
                'images',
                'thumbnail_large',
            )
        }),
        ('Agent Information', {
            'fields': (
                ('agent_name', 'agent_phone'),
                ('agent_email', 'agent_avatar'),
            )
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def thumbnail_preview(self, obj):
        if obj.primary_image:
            return format_html('<img src="{}" style="width: 54px; height: 38px; object-fit: cover; border-radius: 6px;" />', obj.primary_image)
        return "-"
    thumbnail_preview.short_description = "Photo"

    def thumbnail_large(self, obj):
        if obj.primary_image:
            return format_html('<img src="{}" style="max-width: 320px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);" />', obj.primary_image)
        return "-"
    thumbnail_large.short_description = "Main Image Preview"

    def price_display(self, obj):
        if obj.listing_type == 'buy':
            return f"${obj.buy_price:,}"
        return f"${obj.price:,}/mo"
    price_display.short_description = "Price"
