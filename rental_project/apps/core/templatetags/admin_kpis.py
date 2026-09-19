from django import template
from apps.tours.models import DepositReceipt, TourBooking, PaymentSettings
from apps.properties.models import Property
from apps.roommates.models import RoommatePost

register = template.Library()

@register.simple_tag
def get_admin_kpis():
    try:
        pending_receipts = DepositReceipt.objects.filter(status='pending').count()
        approved_receipts = DepositReceipt.objects.filter(status='approved').count()
        confirmed_tours = TourBooking.objects.filter(status='confirmed').count()
        pending_tours = TourBooking.objects.filter(status='pending').count()
        properties_count = Property.objects.count()
        roommates_count = RoommatePost.objects.filter(is_active=True).count()
        payment_settings = PaymentSettings.get_settings()
        recent_pending_receipts = DepositReceipt.objects.filter(status='pending').select_related('booking', 'booking__property')[:5]

        return {
            'pending_receipts_count': pending_receipts,
            'approved_receipts_count': approved_receipts,
            'confirmed_tours_count': confirmed_tours,
            'pending_tours_count': pending_tours,
            'properties_count': properties_count,
            'roommates_count': roommates_count,
            'payment_settings': payment_settings,
            'recent_pending_receipts': recent_pending_receipts,
        }
    except Exception as e:
        return {
            'pending_receipts_count': 0,
            'approved_receipts_count': 0,
            'confirmed_tours_count': 0,
            'pending_tours_count': 0,
            'properties_count': 0,
            'roommates_count': 0,
            'payment_settings': None,
            'recent_pending_receipts': [],
            'error': str(e)
        }
