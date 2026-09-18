from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.properties.models import University

class UserProfile(models.Model):
    USER_TYPES = [
        ('student', 'طالب / طالبة (Student)'),
        ('landlord', 'صاحب سكن / مشرف (Landlord)'),
    ]

    GENDER_CHOICES = [
        ('female', 'أنثى / طالبة'),
        ('male', 'ذكر / طالب'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='student', verbose_name="نوع الحساب")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='female', verbose_name="النوع")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم الهاتف")
    whatsapp = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم الواتساب")
    avatar = models.URLField(
        default='https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=120&w=120',
        verbose_name="صورة البروفايل"
    )
    
    # Student specific fields
    university = models.ForeignKey(
        University,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_profiles',
        verbose_name="الجامعة"
    )
    faculty = models.CharField(max_length=150, blank=True, null=True, verbose_name="الكلية والتخصص")
    academic_year = models.CharField(max_length=50, default="الفرقة الأولى", blank=True, null=True, verbose_name="السنة الدراسية")
    
    # Landlord specific fields
    company_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="اسم الشركة / مكتب السكن")
    bio = models.TextField(blank=True, null=True, verbose_name="نبذة عن السكن والخدمات")
    is_verified = models.BooleanField(default=True, verbose_name="موثق")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        role = "طالب" if self.user_type == 'student' else "صاحب سكن"
        return f"{self.user.get_full_name() or self.user.username} ({role})"

    @property
    def is_landlord(self):
        return self.user_type == 'landlord'

    @property
    def is_student(self):
        return self.user_type == 'student'


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
