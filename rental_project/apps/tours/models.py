from django.db import models
from django.contrib.auth.models import User
from apps.properties.models import Property

class TourBooking(models.Model):
    TOUR_TYPES = [
        ('in_person', 'In-Person Tour'),
        ('video_call', 'Live Video Tour'),
    ]

    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='tour_bookings',
        null=True,
        blank=True
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='tour_bookings',
        null=True,
        blank=True
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    tour_date = models.CharField(max_length=50)
    tour_type = models.CharField(max_length=20, choices=TOUR_TYPES, default='in_person')
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tour Booking"
        verbose_name_plural = "Tour Bookings"
        ordering = ['-created_at']

    def __str__(self):
        prop_title = self.property.title if self.property else "General Inquiry"
        return f"{self.full_name} - {prop_title} ({self.tour_date})"
