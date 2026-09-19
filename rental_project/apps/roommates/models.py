from django.db import models
from django.contrib.auth.models import User
from apps.properties.models import University

class RoommatePost(models.Model):
    GENDER_CHOICES = [
        ('female', 'طالبة (سكن بنات)'),
        ('male', 'طالب (سكن شباب)'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='roommate_posts',
        verbose_name="حساب الطالب المسجل"
    )
    student_name = models.CharField(max_length=150, verbose_name="اسم الطالب/الطالبة")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='female', verbose_name="النوع")
    university = models.ForeignKey(
        University,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='roommate_posts',
        verbose_name="الجامعة"
    )
    faculty = models.CharField(max_length=150, verbose_name="الكلية والتخصص")
    academic_year = models.CharField(max_length=50, default="الفرقة الثانية", verbose_name="السنة الدراسية")
    target_area = models.CharField(max_length=150, verbose_name="المنطقة المفضلة")
    budget_max_egp = models.IntegerField(default=2500, verbose_name="أقصى ميزانية (ج.م/شهر)")
    move_in_date = models.CharField(max_length=50, default="بداية الترم الدراسي", verbose_name="موعد الانتقال")
    sleep_habit = models.CharField(max_length=100, default="هادئ / استذكار منتظم", blank=True, null=True, verbose_name="طبيعة اليوم الدراسي")
    smoking = models.BooleanField(default=False, verbose_name="مدخن")
    bio = models.TextField(verbose_name="مواصفات السكن والزميل المطلوب")
    contact_phone = models.CharField(max_length=50, verbose_name="رقم الهاتف")
    whatsapp_number = models.CharField(max_length=50, verbose_name="رقم الواتساب")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ النشر")

    class Meta:
        verbose_name = "Roommate Post"
        verbose_name_plural = "Roommate Posts"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student_name} ({self.get_gender_display()}) - {self.target_area}"

    def get_whatsapp_url(self):
        clean_num = self.whatsapp_number.replace('+', '').replace(' ', '').replace('-', '')
        msg = f"مرحباً {self.student_name}، رأيت منشورك للبحث عن زميل سكن في {self.target_area} على سكن طلاب القاهرة وأود التواصل معك."
        import urllib.parse
        return f"https://wa.me/{clean_num}?text={urllib.parse.quote(msg)}"
