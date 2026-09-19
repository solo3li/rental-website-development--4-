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
        ('rejected', 'Rejected'),
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tour Booking"
        verbose_name_plural = "Tour Bookings"
        ordering = ['-created_at']

    def __str__(self):
        prop_title = self.property.title if self.property else "General Inquiry"
        return f"{self.full_name} - {prop_title} ({self.tour_date})"


class PaymentSettings(models.Model):
    is_deposit_required = models.BooleanField(default=True, verbose_name="تفعيل إلزامية دفع العربون")
    deposit_amount_egp = models.IntegerField(default=100, verbose_name="قيمة العربون الثابت (ج.م)")
    instapay_address = models.CharField(max_length=100, default='cairo.students@instapay', verbose_name="عنوان InstaPay (IPA)")
    instapay_account_name = models.CharField(max_length=100, default='سكن طلاب القاهرة', verbose_name="اسم المستفيد في InstaPay")
    vodafone_cash_number = models.CharField(max_length=50, default='01012345678', verbose_name="رقم فودافون كاش")
    orange_cash_number = models.CharField(max_length=50, blank=True, null=True, default='01212345678', verbose_name="رقم محفظة بديلة (أورنج/اتصالات/وي)")
    payment_instructions = models.TextField(
        blank=True,
        null=True,
        default='برجاء تحويل مبلغ العربون لتأكيد جدية المعاينة وحجز الموعد، ثم رفع لقطة الشاشة (Screenshot) للتأكيد.',
        verbose_name="تعليمات الدفع المعروضة للطالب"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment Setting"
        verbose_name_plural = "Payment Settings"

    def __str__(self):
        state = "مفعل" if self.is_deposit_required else "معطل"
        return f"إعدادات العربون المركزية ({self.deposit_amount_egp} ج.م - {state})"

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj


class DepositReceipt(models.Model):
    PAYMENT_METHODS = [
        ('instapay', 'InstaPay (إنستاباي)'),
        ('vodafone_cash', 'Vodafone Cash (فودافون كاش)'),
        ('orange_cash', 'Orange Cash (أورنج كاش)'),
        ('etisalat_cash', 'Etisalat Cash (اتصالات كاش)'),
        ('we_pay', 'WE Pay (وي باي)'),
        ('smart_wallet', 'المحافظ البنكية الذكية'),
        ('other', 'طريقة أخرى'),
    ]

    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة ⏳'),
        ('approved', 'معتمد ومقبول ✅'),
        ('rejected', 'مرفوض ❌'),
    ]

    booking = models.OneToOneField(
        TourBooking,
        on_delete=models.CASCADE,
        related_name='deposit_receipt',
        verbose_name="طلب المعاينة / الحجز"
    )
    amount = models.IntegerField(default=100, verbose_name="مبلغ العربون (ج.م)")
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='instapay', verbose_name="وسيلة الدفع")
    sender_info = models.CharField(max_length=100, blank=True, null=True, verbose_name="رقم المحفظة / اسم المحول")
    reference_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="الرقم المرجعي للعملية")
    receipt_image = models.ImageField(upload_to='receipts/%Y/%m/', verbose_name="صورة إيصال التحويل (Screenshot)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="حالة المراجعة")
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="سبب الرفض")
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_receipts', verbose_name="المشرف المراجع")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت المراجعة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الرفع")

    class Meta:
        verbose_name = "Deposit Receipt"
        verbose_name_plural = "Deposit Receipts"
        ordering = ['-created_at']

    def __str__(self):
        return f"إيصال #{self.id} - {self.booking.full_name} ({self.get_status_display()})"
