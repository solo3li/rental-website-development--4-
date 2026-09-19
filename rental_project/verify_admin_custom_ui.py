"""
Verification script for Clean Native Django Admin with Compact Statistics Bar
Tests branding, compact statistics, non-wrapping badges, and admin approval/rejection endpoints.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from apps.properties.models import Property
from apps.tours.models import TourBooking, DepositReceipt, PaymentSettings
from apps.roommates.models import RoommatePost

VALID_JPEG_BYTES = (
    b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00'
    b'\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19'
    b'\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' \",#\x1c\x1c(7),01444\x1f\'9=82<.342'
    b'\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05'
    b'\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07'
    b'\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9'
)

def run_clean_admin_tests():
    print("=" * 70)
    print("🔍 بدء فحص لوحة تحكم دجانغو النظيفة مع شريط الإحصائيات المصغر")
    print("=" * 70)

    client = Client()
    passed = 0
    total = 0

    def assert_test(condition, name, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  ✅ [PASS] {name} {details}")
        else:
            print(f"  ❌ [FAIL] {name} {details}")
            sys.exit(1)

    # 1. Admin Authentication
    print("\n[1] التحقق من تسجيل دخول السوبر أدمن...")
    logged_in = client.login(username='admin', password='Admin@CairoRent2026')
    assert_test(logged_in, "تسجيل دخول السوبر أدمن (admin / Admin@CairoRent2026)")

    # 2. Main Admin Dashboard & Compact Statistics Strip
    print("\n[2] التحقق من الصفحة الرئيسية وشريط الإحصائيات المصغر...")
    res_index = client.get('/admin/')
    assert_test(res_index.status_code == 200, "استجابة صفحة الإدارة الرئيسية", f"HTTP {res_index.status_code}")
    html_index = res_index.content.decode('utf-8')

    assert_test('سكن طلاب القاهرة' in html_index, "ظهور اسم المنصة في شريط العنوان")
    assert_test('مؤشرات منصة سكن الطلاب' in html_index, "ظهور شريط المؤشرات المصغر")
    assert_test('إيصالات قيد المراجعة' in html_index, "بطاقة إحصائية مصغرة للإيصالات المعلقة")
    assert_test('إيصالات معتمدة' in html_index, "بطاقة إحصائية مصغرة للإيصالات المعتمدة")
    assert_test('معاينات مؤكدة' in html_index, "بطاقة إحصائية مصغرة للمعاينات المؤكدة")
    assert_test('سكن الطلاب المسجل' in html_index, "بطاقة إحصائية مصغرة لسكن الطلاب")
    assert_test('رفقاء السكن النشطين' in html_index, "بطاقة إحصائية مصغرة لرفقاء السكن")
    assert_test('app-properties' in html_index or 'Properties' in html_index or 'العقارات' in html_index, "ظهور قائمة الجداول الأصلية النظيفة لجانغو")
    assert_test('recent-actions-module' in html_index, "ظهور سايدبار العمليات الأخيرة النظيف")

    # 3. Deposit Receipts Changelist Table & Status Badges
    print("\n[3] التحقق من جدول إيصالات العربون والشارات الملونة النظيفة...")
    user = User.objects.first()
    prop = Property.objects.first()
    test_booking = TourBooking.objects.create(
        user=user,
        property=prop,
        full_name='طالب فحص الشارات',
        email='badge_test@student.com',
        phone='01022334455',
        tour_date='2026-10-20',
        status='pending'
    )
    receipt_img = SimpleUploadedFile('clean_test_receipt.jpg', VALID_JPEG_BYTES, content_type='image/jpeg')
    test_receipt = DepositReceipt.objects.create(
        booking=test_booking,
        amount=100,
        payment_method='instapay',
        receipt_image=receipt_img,
        status='pending'
    )

    res_receipts = client.get('/admin/tours/depositreceipt/')
    assert_test(res_receipts.status_code == 200, "استجابة جدول إيصالات العربون", f"HTTP {res_receipts.status_code}")
    html_receipts = res_receipts.content.decode('utf-8')

    assert_test('white-space:nowrap' in html_receipts, "تطبيق خاصية منع الالتفاف الرأسي (nowrap) في الشارات")
    assert_test('قيد المراجعة' in html_receipts, "ظهور شارة قيد المراجعة")
    assert_test('قبول ✅' in html_receipts, "ظهور زر قبول المباشر")
    assert_test('رفض ❌' in html_receipts, "ظهور زر رفض المباشر")

    # 4. Quick Approval Test
    print("\n[4] تجربة زر القبول السريع للإيصال...")
    approve_url = reverse('admin:tours_depositreceipt_approve', args=[test_receipt.id])
    res_appr = client.get(approve_url)
    assert_test(res_appr.status_code == 302, "إعادة التوجيه بعد الاعتماد", f"Redirect {res_appr.status_code}")
    test_receipt.refresh_from_db()
    test_booking.refresh_from_db()
    assert_test(test_receipt.status == 'approved', "تحول حالة الإيصال إلى معتمد")
    assert_test(test_booking.status == 'confirmed', "تأكيد موعد المعاينة تلقائياً")

    # 5. Properties Table & Beds Badges
    print("\n[5] التحقق من جدول العقارات وشارات الأسِرّة...")
    res_props = client.get('/admin/properties/property/')
    assert_test(res_props.status_code == 200, "استجابة جدول سكن الطلاب", f"HTTP {res_props.status_code}")
    html_props = res_props.content.decode('utf-8')
    assert_test('الأسِرّة الشاغرة' in html_props or 'الأسِرّة' in html_props, "عمود الأسِرّة الشاغرة")

    # 6. Payment Settings Admin
    print("\n[6] التحقق من لوحة إعدادات الدفع المركزية...")
    res_settings = client.get('/admin/tours/paymentsettings/')
    assert_test(res_settings.status_code == 200, "استجابة إعدادات الدفع", f"HTTP {res_settings.status_code}")

    # 7. TourBooking Admin Page & WhatsApp / Status Badges
    print("\n[7] التحقق من تحسينات لوحة حجوزات المعاينة (TourBooking)...")
    res_tours = client.get('/admin/tours/tourbooking/')
    assert_test(res_tours.status_code == 200, "استجابة جدول حجوزات المعاينة", f"HTTP {res_tours.status_code}")
    html_tours = res_tours.content.decode('utf-8')
    assert_test('💬 واتساب' in html_tours, "ظهور زر مراسلة الواتساب المباشر")
    assert_test('wa.me' in html_tours, "توليد رابط الواتساب الصحيح للطالب")
    assert_test('ميدانية' in html_tours or 'فيديو' in html_tours, "ظهور شارة نوع المعاينة")
    assert_test('مؤكد' in html_tours, "ظهور شارة حالة المعاينة الملونة")
    # 8. UserProfile Admin Page & Avatar / Badges / WhatsApp
    print("\n[8] التحقق من تحسينات لوحة ملفات المستخدمين (UserProfile)...")
    res_profiles = client.get('/admin/accounts/userprofile/')
    assert_test(res_profiles.status_code == 200, "استجابة جدول ملفات المستخدمين", f"HTTP {res_profiles.status_code}")
    html_profiles = res_profiles.content.decode('utf-8')
    assert_test('border-radius:50%' in html_profiles, "ظهور صورة البروفايل الرمزية (Avatar) الدائرية")
    assert_test('طالب' in html_profiles or 'صاحب سكن' in html_profiles, "ظهور شارة نوع الحساب الملونة")
    assert_test('موثق' in html_profiles or 'قيد التحقق' in html_profiles, "ظهور شارة التوثيق")
    assert_test('verify_selected_profiles' in html_profiles, "وجود خيار التوثيق المجمع للحسابات")

    # 9. RoommatePost Admin Page & Badges / WhatsApp / Bio / Actions
    print("\n[9] التحقق من تحسينات لوحة إعلانات زملاء السكن (RoommatePost)...")
    admin_user = User.objects.filter(is_superuser=True).first()
    post_with_user = RoommatePost.objects.filter(user__isnull=False).first()
    if not post_with_user:
        first_post = RoommatePost.objects.first()
        if first_post:
            first_post.user = admin_user
            first_post.save()
        else:
            RoommatePost.objects.create(
                user=admin_user,
                student_name="نور أحمد",
                gender="female",
                faculty="طب قصر العيني",
                target_area="الدقي",
                budget_max_egp=3000,
                bio="أبحث عن زميلة سكن هادئة وملتزمة في شقة قريبة من المترو",
                contact_phone="01012345678",
                whatsapp_number="01012345678",
                smoking=False,
                is_active=True
            )
    res_rm = client.get('/admin/roommates/roommatepost/')
    assert_test(res_rm.status_code == 200, "استجابة جدول إعلانات زملاء السكن", f"HTTP {res_rm.status_code}")
    html_rm = res_rm.content.decode('utf-8')
    assert_test('💬 واتساب' in html_rm, "ظهور زر مراسلة الواتساب المباشر لزميل السكن")
    assert_test('wa.me' in html_rm, "توليد رابط واتساب مع رسالة جاهزة")
    assert_test('طالبة (بنات)' in html_rm or 'طالب (شباب)' in html_rm, "ظهور شارة النوع الملونة")
    assert_test('غير مدخن' in html_rm or 'مدخن' in html_rm, "ظهور شارة التدخين")
    assert_test('ج.م / شهر' in html_rm, "تنسيق الميزانية المالية")
    assert_test('make_active' in html_rm and 'make_inactive' in html_rm, "ظهور الأكشنز الجماعية للتنشيط والإيقاف")
    assert_test('title="عرض حساب المستخدم في لوحة التحكم"' in html_rm or '(@' in html_rm, "ربط الحساب المسجل ببروفايله في الأدمن")

    # 10. Bilingual Support & Language Switcher (AR & EN)
    print("\n[10] التحقق من دعم اللغتين العربية والإنجليزية وزر التبديل السريع...")
    # A) Check Arabic interface by default
    res_ar = client.get('/admin/')
    assert_test(res_ar.status_code == 200, "استجابة لوحة التحكم باللغة العربية")
    html_ar = res_ar.content.decode('utf-8')
    assert_test('سكن طلاب القاهرة — لوحة الإدارة' in html_ar, "ظهور عنوان اللوحة بالعربية")
    assert_test('مؤشرات منصة سكن الطلاب' in html_ar, "ظهور شريط المؤشرات بالعربية")
    assert_test('🌐 English' in html_ar, "ظهور زر التبديل إلى الإنجليزية (🌐 English)")

    # B) Switch language to English via set_language
    res_setlang = client.post('/i18n/setlang/', {'language': 'en', 'next': '/admin/'})
    assert_test(res_setlang.status_code == 302, "إعادة التوجيه بعد تغيير اللغة إلى الإنجليزية")

    # C) Verify English interface
    res_en = client.get('/admin/')
    assert_test(res_en.status_code == 200, "استجابة لوحة التحكم باللغة الإنجليزية")
    html_en = res_en.content.decode('utf-8')
    assert_test('Cairo Student Housing — Admin Panel' in html_en, "ظهور عنوان اللوحة بالإنجليزية")
    assert_test('Student Housing Platform Metrics' in html_en, "ظهور شريط المؤشرات بالإنجليزية")
    assert_test('🌐 العربية' in html_en, "ظهور زر التبديل إلى العربية (🌐 العربية)")

    # D) Verify RoommatePost table in English
    res_rm_en = client.get('/admin/roommates/roommatepost/')
    assert_test(res_rm_en.status_code == 200, "استجابة جدول إعلانات زملاء السكن بالإنجليزية")
    html_rm_en = res_rm_en.content.decode('utf-8')
    assert_test('Female Student' in html_rm_en or 'Male Student' in html_rm_en, "ترجمة شارة النوع إلى الإنجليزية")
    assert_test('Non-smoker' in html_rm_en or 'Smoker' in html_rm_en, "ترجمة شارة التدخين إلى الإنجليزية")
    assert_test('EGP / mo' in html_rm_en, "ترجمة عملة الميزانية إلى الإنجليزية (EGP / mo)")
    assert_test('💬 WhatsApp' in html_rm_en, "ترجمة زر الواتساب إلى الإنجليزية")
    assert_test('Active' in html_rm_en or 'Inactive' in html_rm_en, "ترجمة شارة الحالة إلى الإنجليزية")

    # E) Verify UserProfile table in English
    res_prof_en = client.get('/admin/accounts/userprofile/')
    assert_test(res_prof_en.status_code == 200, "استجابة جدول ملفات المستخدمين بالإنجليزية")
    html_prof_en = res_prof_en.content.decode('utf-8')
    assert_test('Student 🎓' in html_prof_en or 'Landlord 🏢' in html_prof_en, "ترجمة نوع الحساب إلى الإنجليزية")
    assert_test('Verified ✅' in html_prof_en or 'Pending Verification ⚠️' in html_prof_en, "ترجمة شارة التوثيق إلى الإنجليزية")

    # F) Switch back to Arabic to ensure full roundtrip
    res_back_ar = client.post('/i18n/setlang/', {'language': 'ar', 'next': '/admin/'})
    assert_test(res_back_ar.status_code == 302, "إعادة التوجيه بعد العودة للغة العربية")
    res_ar_final = client.get('/admin/')
    html_ar_final = res_ar_final.content.decode('utf-8')
    assert_test('سكن طلاب القاهرة — لوحة الإدارة' in html_ar_final, "العودة للواجهة العربية بنجاح")

    print("\n" + "=" * 70)
    print(f"🎉 تم اجتياز جميع الفحوصات بنجاح تام! ({passed}/{total} Tests Passed)")
    print("=" * 70)

if __name__ == '__main__':
    run_clean_admin_tests()
