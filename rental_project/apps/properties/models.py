from django.contrib.gis.db import models as gis_models
from django.db import models
from django.contrib.gis.geos import Point

class Property(gis_models.Model):
    PROPERTY_TYPES = [
        ('House', 'House'),
        ('Apartment', 'Apartment'),
        ('Villa', 'Villa'),
        ('Townhouse', 'Townhouse'),
        ('Studio', 'Studio'),
    ]

    LISTING_TYPES = [
        ('rent', 'Rent'),
        ('buy', 'Buy'),
    ]

    RENTAL_PERIODS = [
        ('month', 'Month'),
        ('week', 'Week'),
        ('year', 'Year'),
    ]

    title = models.CharField(max_length=255)
    title_ar = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    description_ar = models.TextField(blank=True, null=True)
    
    price = models.IntegerField(help_text="Monthly rent in USD")
    buy_price = models.IntegerField(default=150000, help_text="Total purchase price in USD")
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPES, default='rent')
    rental_period = models.CharField(max_length=20, choices=RENTAL_PERIODS, default='month')
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES, default='Apartment')
    
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50, default='US')
    
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.IntegerField(default=1)
    area_sqft = models.IntegerField(default=1000)
    
    images = models.JSONField(default=list, help_text="List of image URLs")
    featured = models.BooleanField(default=False)
    badge = models.CharField(max_length=50, default="Perfect Fit", blank=True, null=True)
    posted_days_ago = models.IntegerField(default=1)
    
    is_family_friendly = models.BooleanField(default=True)
    family_highlights = models.JSONField(default=list, blank=True, null=True)
    amenities = models.JSONField(default=list, help_text="List of amenities strings")
    
    agent_name = models.CharField(max_length=100, default="Sarah Jenkins")
    agent_phone = models.CharField(max_length=50, default="+1 (555) 234-5678")
    agent_email = models.EmailField(default="sarah.agent@horizonrealty.com")
    agent_avatar = models.URLField(default="https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=120&w=120")
    
    lat = models.CharField(max_length=50, default="40.7128")
    lng = models.CharField(max_length=50, default="-74.0060")
    
    # PostGIS spatial point for GeoDjango map widget in Admin and spatial queries
    location = gis_models.PointField(srid=4326, geography=True, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Sync lat/lng with PostGIS geometry
        if self.location:
            self.lat = str(self.location.y)
            self.lng = str(self.location.x)
        elif self.lat and self.lng:
            try:
                self.location = Point(float(self.lng), float(self.lat), srid=4326)
            except (ValueError, TypeError):
                pass
        super().save(*args, **kwargs)

    @property
    def primary_image(self):
        if self.images and len(self.images) > 0:
            return self.images[0]
        return "https://images.pexels.com/photos/8134745/pexels-photo-8134745.jpeg"

    def get_title(self, is_ar=False):
        if is_ar and self.title_ar:
            return self.title_ar
        return self.title

    def get_description(self, is_ar=False):
        if is_ar and self.description_ar:
            return self.description_ar
        return self.description

    def __str__(self):
        return f"{self.title} ({self.city}, {self.state})"
