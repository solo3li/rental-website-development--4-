"""
Comprehensive End-to-End Test Script for Manual Deposit System (العربون اليدوي)
Tests complete flow strictly via Django test client and database models.
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from apps.properties.models import Property
from apps.tours.models import TourBooking, DepositReceipt, PaymentSettings

# Minimal valid 1x1 JPEG for receipt testing
VALID_JPEG_BYTES = (
    b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00'
    b'\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19'
    b'\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' \",#\x1c\x1c(7),01444\x1f\'9=82<.342'
    b'\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05'
    b'\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07'
    b'\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9'
)

def run_tests():
    print("=" * 65)
    print("🚀 بدء تشغيل الفحص الشامل لنظام العربون اليدوي (End-to-End Test)")
    print("=" * 65)

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

    # -------------------------------------------------------------
    # 1. Admin Authentication with New Password
    # -------------------------------------------------------------
    print("\n[1] التحقق من تسجيل دخول السوبر أدمن بكلمة المرور الجديدة...")
    login_success = client.login(username='admin', password='Admin@CairoRent2026')
    assert_test(login_success, "تسجيل دخول السوبر أدمن", "(admin / Admin@CairoRent2026)")

    # -------------------------------------------------------------
    # 2. Admin Deposit Panel UI Endpoints
    # -------------------------------------------------------------
    print("\n[2] التحقق من صفحات لوحة التحكم المخصصة (Custom Admin UI)...")
    
    res_receipts = client.get('/admin/tours/depositreceipt/')
    assert_test(res_receipts.status_code == 200, "لوحة إيصالات العربون (Deposit Receipts Changelist)", f"HTTP {res_receipts.status_code}")
    assert_test('إيصالات العربون' in res_receipts.content.decode('utf-8') or 'Deposit Receipts' in res_receipts.content.decode('utf-8'), "عنوان لوحة الإيصالات موجود")

    res_settings = client.get('/admin/tours/paymentsettings/')
    assert_test(res_settings.status_code == 200, "صفحة إعدادات الدفع المركزية (Payment Settings)", f"HTTP {res_settings.status_code}")

    res_tours = client.get('/admin/tours/tourbooking/')
    assert_test(res_tours.status_code == 200, "لوحة حجوزات المعاينة (Tour Bookings)", f"HTTP {res_tours.status_code}")

    # -------------------------------------------------------------
    # 3. Verify / Configure PaymentSettings
    # -------------------------------------------------------------
    print("\n[3] التحقق من إعدادات محافظ الدفع المركزية...")
    settings = PaymentSettings.get_settings()
    settings.is_deposit_required = True
    settings.deposit_amount_egp = 100
    settings.instapay_address = 'cairo.students@instapay'
    settings.instapay_account_name = 'سكن طلاب القاهرة'
    settings.vodafone_cash_number = '01012345678'
    settings.save()
    assert_test(settings.is_deposit_required is True, "العربون مفعل إجبارياً")
    assert_test(settings.deposit_amount_egp == 100, "قيمة العربون 100 ج.م")
    assert_test(settings.instapay_address == 'cairo.students@instapay', "عنوان InstaPay")

    # -------------------------------------------------------------
    # 4. Student User & Tour Booking Flow with Receipt Upload
    # -------------------------------------------------------------
    print("\n[4] تجربة تقديم حجز معاينة من طالب ورفع سكرين شوت الإيصال...")
    student_user, _ = User.objects.get_or_create(username='test_student_e2e', defaults={'email': 'student_e2e@cairo.edu'})
    student_user.set_password('studentpass123')
    student_user.save()

    prop = Property.objects.first()
    assert_test(prop is not None, "وجود سكن في قاعدة البيانات لربط الحجز به", f"ID={prop.id} - {prop.title}")

    # Switch to student client
    student_client = Client()
    student_client.force_login(student_user)

    # A) Attempt booking without receipt -> Should FAIL with 400
    res_no_receipt = student_client.post('/tours/book/?format=json', {
        'property': prop.id,
        'full_name': 'حازم محمد الطالب',
        'email': 'student_e2e@cairo.edu',
        'phone': '01099887766',
        'tour_date': '2026-10-10',
        'tour_type': 'in_person',
        'message': 'معاينة الغرفة المفردة',
    }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert_test(res_no_receipt.status_code == 400, "رفض الحجز عند غياب إيصال العربون", f"HTTP {res_no_receipt.status_code}")

    # B) Submit booking WITH receipt -> Should SUCCEED with 200
    receipt_file = SimpleUploadedFile('student_receipt.jpg', VALID_JPEG_BYTES, content_type='image/jpeg')
    res_with_receipt = student_client.post('/tours/book/?format=json', {
        'property': prop.id,
        'full_name': 'حازم محمد الطالب',
        'email': 'student_e2e@cairo.edu',
        'phone': '01099887766',
        'tour_date': '2026-10-10',
        'tour_type': 'in_person',
        'payment_method': 'instapay',
        'sender_info': '01099887766',
        'reference_number': 'INSTA-998822',
        'receipt_image': receipt_file,
        'message': 'معاينة الغرفة المفردة مع إيصال انستاباي',
    }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    assert_test(res_with_receipt.status_code == 200, "نجاح الحجز بعد إرفاق إيصال الدفع", f"HTTP {res_with_receipt.status_code}")
    json_resp = res_with_receipt.json()
    assert_test(json_resp.get('success') is True, "استجابة JSON تؤكد نجاح الطلب")

    # Verify DB records
    booking = TourBooking.objects.filter(email='student_e2e@cairo.edu').latest('created_at')
    assert_test(booking.status == 'pending', "حالة الحجز مبدئياً: قيد المراجعة (pending)")
    assert_test(hasattr(booking, 'deposit_receipt'), "ربط إيصال العربون بطلب الحجز بنجاح (OneToOne)")
    
    receipt = booking.deposit_receipt
    assert_test(receipt.status == 'pending', "حالة الإيصال: قيد المراجعة (pending)")
    assert_test(receipt.amount == 100, "مبلغ الإيصال 100 ج.م")
    assert_test(receipt.payment_method == 'instapay', "وسيلة الدفع: instapay")
    assert_test(bool(receipt.receipt_image), "تم حفظ ملف صورة الإيصال في Media")

    # -------------------------------------------------------------
    # 5. Admin Approve Flow (قبول الإيصال وتأكيد الحجز)
    # -------------------------------------------------------------
    print("\n[5] تجربة قرار الأدمن: [قبول الإيصال وتأكيد الحجز] بنقرة واحدة...")
    approve_url = reverse('admin:tours_depositreceipt_approve', args=[receipt.id])
    res_approve = client.get(approve_url)
    assert_test(res_approve.status_code == 302, "إعادة توجيه ناجحة بعد القبول (Redirect 302)")

    receipt.refresh_from_db()
    booking.refresh_from_db()
    admin_user = User.objects.get(username='admin')

    assert_test(receipt.status == 'approved', "تحديث حالة الإيصال إلى: معتمد ومقبول (approved)")
    assert_test(receipt.reviewed_by == admin_user, "تسجيل المشرف الذي راجع الإيصال (admin)")
    assert_test(receipt.reviewed_at is not None, "تسجيل التوقيت الزمني للمراجعة")
    assert_test(booking.status == 'confirmed', "تأكيد موعد المعاينة تلقائياً (confirmed)")

    # -------------------------------------------------------------
    # 6. Admin Reject Flow (رفض الإيصال وإلغاء الطلب مع السبب)
    # -------------------------------------------------------------
    print("\n[6] تجربة قرار الأدمن: [رفض الإيصال وإلغاء الطلب]...")
    booking_to_reject = TourBooking.objects.create(
        user=student_user,
        property=prop,
        full_name='طالب تم رفض إيصاله',
        email='rejected_student@cairo.edu',
        phone='01011112222',
        tour_date='2026-10-12',
        status='pending'
    )
    receipt_file_rej = SimpleUploadedFile('reject_receipt.jpg', VALID_JPEG_BYTES, content_type='image/jpeg')
    receipt_to_reject = DepositReceipt.objects.create(
        booking=booking_to_reject,
        amount=100,
        payment_method='vodafone_cash',
        receipt_image=receipt_file_rej,
        status='pending'
    )

    reject_url = reverse('admin:tours_depositreceipt_reject', args=[receipt_to_reject.id])
    res_reject = client.get(reject_url)
    assert_test(res_reject.status_code == 302, "إعادة توجيه ناجحة بعد الرفض (Redirect 302)")

    receipt_to_reject.refresh_from_db()
    booking_to_reject.refresh_from_db()

    assert_test(receipt_to_reject.status == 'rejected', "تحديث حالة الإيصال إلى: مرفوض (rejected)")
    assert_test(booking_to_reject.status == 'rejected', "تحديث حالة الحجز إلى: مرفوض (rejected)")
    assert_test(len(receipt_to_reject.rejection_reason) > 0, "تسجيل سبب الرفض في قاعدة البيانات", f"'{receipt_to_reject.rejection_reason}'")

    # -------------------------------------------------------------
    # 7. Student Profile Template Render Check
    # -------------------------------------------------------------
    print("\n[7] فحص ظهور حالة العربون والإيصال في بروفايل الطالب...")
    res_profile = student_client.get('/accounts/profile/?tab=tours')
    assert_test(res_profile.status_code == 200, "فتح صفحة بروفايل الطالب (تبويب المعاينات)", f"HTTP {res_profile.status_code}")
    profile_html = res_profile.content.decode('utf-8')
    assert_test('عربون الحجز' in profile_html or 'عربون المعاينة' in profile_html, "ظهور بطاقة تفاصيل العربون")
    assert_test('إيصال معتمد' in profile_html, "ظهور شارة إيصال معتمد ✅")
    assert_test('عرض الإيصال' in profile_html, "ظهور رابط عرض صورة الإيصال")

    print("\n" + "=" * 65)
    print(f"🎉 تم اجتياز جميع الفحوصات بنجاح تام! ({passed}/{total} Tests Passed)")
    print("=" * 65)

if __name__ == '__main__':
    run_tests()
