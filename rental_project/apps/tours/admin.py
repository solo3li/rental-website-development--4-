from django.contrib import admin
from .models import TourBooking

@admin.register(TourBooking)
class TourBookingAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'property', 'tour_date', 'tour_type', 'phone', 'email', 'status', 'created_at')
    list_filter = ('tour_type', 'status', 'tour_date')
    search_fields = ('full_name', 'email', 'phone', 'property__title')
    readonly_fields = ('created_at',)
