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
    assert_test('confirm_selected_tours' in html_tours, "وجود خيار الإجراء المجمع لتأكيد المواعيد")

    print("\n" + "=" * 70)
    print(f"🎉 تم اجتياز جميع الفحوصات بنجاح تام! ({passed}/{total} Tests Passed)")
    print("=" * 70)

if __name__ == '__main__':
    run_clean_admin_tests()
