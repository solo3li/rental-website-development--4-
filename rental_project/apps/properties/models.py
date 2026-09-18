from django.contrib.gis.db import models as gis_models
from django.db import models
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User

class University(gis_models.Model):
    name = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255)
    short_code = models.CharField(max_length=20, blank=True, null=True)  # CU, ASU, GUC, AUC, etc.
    city = models.CharField(max_length=100, default='القاهرة')
    address = models.CharField(max_length=255, blank=True, null=True)
    lat = models.CharField(max_length=50, default="30.0276")
    lng = models.CharField(max_length=50, default="31.2089")
    location = gis_models.PointField(srid=4326, geography=True, null=True, blank=True)
    nearest_metro = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "University"
        verbose_name_plural = "Universities"
        ordering = ['name_ar']

    def __str__(self):
        return self.name_ar or self.name

    def save(self, *args, **kwargs):
        if self.location:
            self.lat = str(self.location.y)
            self.lng = str(self.location.x)
        elif self.lat and self.lng:
            try:
                self.location = Point(float(self.lng), float(self.lat), srid=4326)
            except (ValueError, TypeError):
                pass
        super().save(*args, **kwargs)


class MetroStation(gis_models.Model):
    LINES = [
        ('line_1', 'الخط الأول (حلوان - المرج)'),
        ('line_2', 'الخط الثاني (شبرا - المنيب)'),
        ('line_3', 'الخط الثالث (عدلي منصور - إمبابة / جامعة القاهرة)'),
    ]

    name = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    line = models.CharField(max_length=50, choices=LINES, default='line_2')
    lat = models.CharField(max_length=50, default="30.0382")
    lng = models.CharField(max_length=50, default="31.2119")
    location = gis_models.PointField(srid=4326, geography=True, null=True, blank=True)

    class Meta:
        verbose_name = "Metro Station"
        verbose_name_plural = "Metro Stations"
        ordering = ['name_ar']

    def __str__(self):
        return f"محطة {self.name_ar} ({self.get_line_display()})"

    def save(self, *args, **kwargs):
        if self.location:
            self.lat = str(self.location.y)
            self.lng = str(self.location.x)
        elif self.lat and self.lng:
            try:
                self.location = Point(float(self.lng), float(self.lat), srid=4326)
            except (ValueError, TypeError):
                pass
        super().save(*args, **kwargs)


class Property(gis_models.Model):
    RENTAL_TYPES = [
        ('bed', 'سرير في غرفة مشتركة / Bed in Shared Room'),
        ('room', 'غرفة خاصة بسكن مشترك / Private Room'),
        ('apartment', 'شقة كاملة للطلاب / Full Apartment'),
    ]

    GENDER_POLICIES = [
        ('female_only', 'سكن طالبات (بنات فقط) / Female Only'),
        ('male_only', 'سكن طلاب (شباب فقط) / Male Only'),
        ('any', 'متاح للجميع / Open to All'),
    ]

    PROPERTY_TYPES = [
        ('Apartment', 'Apartment / شقة'),
        ('Studio', 'Studio / ستوديو'),
        ('House', 'Student Dorm / سكن جماعي'),
        ('Villa', 'Villa'),
        ('Townhouse', 'Townhouse'),
    ]

    LISTING_TYPES = [
        ('rent', 'Rent'),
        ('buy', 'Buy'),
    ]

    RENTAL_PERIODS = [
        ('month', 'شهر / Month'),
        ('semester', 'ترم دراسي / Semester'),
        ('year', 'سنة دراسية / Year'),
    ]

    title = models.CharField(max_length=255)
    title_ar = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    description_ar = models.TextField(blank=True, null=True)
    
    # Pricing in EGP (Egyptian Pounds)
    price_egp = models.IntegerField(default=2500, help_text="الإيجار الشهري بالجنيه المصري")
    deposit_egp = models.IntegerField(default=2000, help_text="مبلغ التأمين بالجنيه")
    bills_included = models.BooleanField(default=True, help_text="شامل الفواتير (كهرباء، مياه، غاز، إنترنت)")
    
    # Backward compatibility fields
    price = models.IntegerField(default=2500, help_text="Monthly rent (sync with price_egp)")
    buy_price = models.IntegerField(default=150000)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPES, default='rent')
    rental_period = models.CharField(max_length=20, choices=RENTAL_PERIODS, default='month')
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES, default='Apartment')
    
    # Student specific housing specs
    rental_type = models.CharField(max_length=20, choices=RENTAL_TYPES, default='bed')
    gender_policy = models.CharField(max_length=20, choices=GENDER_POLICIES, default='female_only')
    total_capacity = models.IntegerField(default=4, help_text="إجمالي سعة الأسِرّة بالسكن")
    available_beds = models.IntegerField(default=2, help_text="عدد الأسِرّة المتاحة حالياً")
    
    # University & Metro Proximity (PostGIS)
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True, blank=True, related_name='properties')
    nearest_metro = models.ForeignKey(MetroStation, on_delete=models.SET_NULL, null=True, blank=True, related_name='properties')
    distance_to_university_km = models.FloatField(default=0.8, help_text="المسافة للجامعة بالكيلومتر")
    walking_minutes = models.IntegerField(default=10, help_text="وقت السير للجامعة بالدقائق")

    # Location
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100, default="القاهرة")
    state = models.CharField(max_length=100, default="القاهرة")
    zip_code = models.CharField(max_length=20, default="12613")
    country = models.CharField(max_length=50, default='EG')
    
    bedrooms = models.IntegerField(default=2)
    bathrooms = models.IntegerField(default=1)
    area_sqft = models.IntegerField(default=120)  # In sqm
    floor_number = models.IntegerField(default=3)
    has_elevator = models.BooleanField(default=True)
    
    # Student Amenities
    study_desk = models.BooleanField(default=True, help_text="مكتب مذاكرة مخصص")
    wifi_speed = models.CharField(max_length=50, default="30 Mbps Wi-Fi", blank=True, null=True)
    curfew_time = models.CharField(max_length=50, default="11:00 PM", blank=True, null=True, help_text="ميعاد غلق الباب الخارجي")
    is_supervised = models.BooleanField(default=True, help_text="إشراف وأمن على السكن")
    
    images = models.JSONField(default=list, help_text="List of image URLs")
    featured = models.BooleanField(default=False)
    badge = models.CharField(max_length=50, default="مميز للطلاب", blank=True, null=True)
    posted_days_ago = models.IntegerField(default=1)
    
    is_family_friendly = models.BooleanField(default=False)
    family_highlights = models.JSONField(default=list, blank=True, null=True)
    amenities = models.JSONField(default=list, help_text="List of amenities strings")
    
    # Contact information for instant WhatsApp & Direct Call
    agent_name = models.CharField(max_length=100, default="أحمد عثمان (مشرف السكن)")
    agent_phone = models.CharField(max_length=50, default="+201012345678")
    whatsapp_number = models.CharField(max_length=50, default="+201012345678")
    agent_email = models.EmailField(default="contact@sakancairo.com")
    agent_avatar = models.URLField(default="https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=120&w=120")
    
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_properties')
    
    lat = models.CharField(max_length=50, default="30.0276")
    lng = models.CharField(max_length=50, default="31.2089")
    
    # PostGIS spatial point for GeoDjango map widget in Admin and spatial queries
    location = gis_models.PointField(srid=4326, geography=True, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Student Property"
        verbose_name_plural = "Student Properties"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Sync price with price_egp
        if self.price_egp:
            self.price = self.price_egp
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

    def get_gender_display_ar(self):
        mapping = {
            'female_only': 'سكن طالبات (بنات فقط)',
            'male_only': 'سكن طلاب (شباب فقط)',
            'any': 'متاح للجميع',
        }
        return mapping.get(self.gender_policy, 'سكن طلاب')

    def get_rental_type_display_ar(self):
        mapping = {
            'bed': 'سرير بغرفة مشتركة',
            'room': 'غرفة خاصة',
            'apartment': 'شقة كاملة',
        }
        return mapping.get(self.rental_type, 'سكن طلابي')

    def get_whatsapp_url(self, is_ar=True):
        clean_number = self.whatsapp_number.replace('+', '').replace(' ', '').replace('-', '')
        text = f"مرحباً، أود الاستفسار عن {self.title_ar or self.title} المعروض على سكن طلاب القاهرة (كود #{self.id})." if is_ar else f"Hello, I am inquiring about {self.title} on Cairo Student Living (Code #{self.id})."
        import urllib.parse
        encoded_text = urllib.parse.quote(text)
        return f"https://wa.me/{clean_number}?text={encoded_text}"

    def __str__(self):
        return f"{self.title} ({self.city}) - {self.get_gender_display_ar()}"
