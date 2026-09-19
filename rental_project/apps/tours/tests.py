from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from apps.properties.models import Property
from apps.tours.models import TourBooking, DepositReceipt, PaymentSettings

# Minimal valid 1x1 pixel JPEG
VALID_JPEG_BYTES = (
    b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00'
    b'\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19'
    b'\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' \",#\x1c\x1c(7),01444\x1f\'9=82<.342'
    b'\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05'
    b'\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07'
    b'\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9'
)

class ToursAppTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tourstudent', email='tour@student.com', password='password123')
        self.user.profile.phone = '01011223344'
        self.user.profile.save()

        self.admin_user = User.objects.create_superuser(username='superadmin', email='admin@test.com', password='adminpassword')

        self.prop = Property.objects.create(
            title='Sample Cairo Dorm',
            price_egp=2200,
            address='بين السرايات',
            city='الجيزة'
        )

        self.settings = PaymentSettings.get_settings()
        self.settings.is_deposit_required = True
        self.settings.deposit_amount_egp = 100
        self.settings.instapay_address = 'cairohousing@instapay'
        self.settings.vodafone_cash_number = '01000000001'
        self.settings.save()

    def test_tour_booking_requires_receipt_when_deposit_enabled(self):
        """When deposit is required, booking without receipt image fails validation"""
        client = Client()
        client.force_login(self.user)

        response = client.post('/tours/book/?format=json', {
            'property': self.prop.id,
            'full_name': 'طالب تجريبي',
            'email': 'tour@student.com',
            'phone': '01011223344',
            'tour_date': '2026-10-01',
            'tour_type': 'in_person',
            'message': 'أريد المعاينة',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 400)
        json_data = response.json()
        self.assertFalse(json_data.get('success', True))
        self.assertIn('receipt_image', json_data.get('errors', {}))

    def test_tour_booking_with_receipt_creates_booking_and_receipt(self):
        """Submitting booking with receipt image creates pending TourBooking and DepositReceipt"""
        client = Client()
        client.force_login(self.user)

        receipt_file = SimpleUploadedFile('receipt.jpg', VALID_JPEG_BYTES, content_type='image/jpeg')

        response = client.post('/tours/book/?format=json', {
            'property': self.prop.id,
            'full_name': 'أحمد إبراهيم',
            'email': 'ahmed@student.com',
            'phone': '01012345678',
            'tour_date': '2026-10-05',
            'tour_type': 'in_person',
            'payment_method': 'instapay',
            'sender_info': '01012345678',
            'reference_number': 'REF123456',
            'receipt_image': receipt_file,
            'message': 'معاينة الغرفة المزدوجة',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data.get('success'))

        booking = TourBooking.objects.filter(email='ahmed@student.com').first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.status, 'pending')
        self.assertEqual(booking.user, self.user)

        receipt = booking.deposit_receipt
        self.assertIsNotNone(receipt)
        self.assertEqual(receipt.status, 'pending')
        self.assertEqual(receipt.amount, 100)
        self.assertEqual(receipt.payment_method, 'instapay')
        self.assertEqual(receipt.reference_number, 'REF123456')
        self.assertTrue(bool(receipt.receipt_image))

    def test_admin_approve_receipt_updates_booking_status(self):
        """Admin approving receipt confirms booking and updates receipt status"""
        booking = TourBooking.objects.create(
            user=self.user,
            property=self.prop,
            full_name='أحمد إبراهيم',
            email='ahmed@student.com',
            phone='01012345678',
            tour_date='2026-10-05',
            status='pending'
        )
        receipt_file = SimpleUploadedFile('receipt.jpg', VALID_JPEG_BYTES, content_type='image/jpeg')
        receipt = DepositReceipt.objects.create(
            booking=booking,
            amount=100,
            payment_method='instapay',
            receipt_image=receipt_file,
            status='pending'
        )

        client = Client()
        client.force_login(self.admin_user)

        approve_url = reverse('admin:tours_depositreceipt_approve', args=[receipt.id])
        response = client.get(approve_url)
        self.assertEqual(response.status_code, 302)

        receipt.refresh_from_db()
        booking.refresh_from_db()

        self.assertEqual(receipt.status, 'approved')
        self.assertEqual(receipt.reviewed_by, self.admin_user)
        self.assertIsNotNone(receipt.reviewed_at)
        self.assertEqual(booking.status, 'confirmed')

    def test_admin_reject_receipt_cancels_booking_with_reason(self):
        """Admin rejecting receipt marks booking rejected and records reason"""
        booking = TourBooking.objects.create(
            user=self.user,
            property=self.prop,
            full_name='أحمد إبراهيم',
            email='ahmed@student.com',
            phone='01012345678',
            tour_date='2026-10-05',
            status='pending'
        )
        receipt_file = SimpleUploadedFile('receipt.jpg', VALID_JPEG_BYTES, content_type='image/jpeg')
        receipt = DepositReceipt.objects.create(
            booking=booking,
            amount=100,
            payment_method='instapay',
            receipt_image=receipt_file,
            status='pending'
        )

        client = Client()
        client.force_login(self.admin_user)

        reject_url = reverse('admin:tours_depositreceipt_reject', args=[receipt.id])
        response = client.get(reject_url)
        self.assertEqual(response.status_code, 302)

        receipt.refresh_from_db()
        booking.refresh_from_db()

        self.assertEqual(receipt.status, 'rejected')
        self.assertEqual(booking.status, 'rejected')
        self.assertTrue(len(receipt.rejection_reason) > 0)
        self.assertEqual(receipt.reviewed_by, self.admin_user)

    def test_tour_cancellation_authorization(self):
        """Verify user can cancel their own tour booking"""
        booking = TourBooking.objects.create(
            user=self.user,
            property=self.prop,
            full_name='طالب تجريبي',
            email='tour@student.com',
            phone='01011223344',
            tour_date='2026-10-01',
            status='pending'
        )

        other_user = User.objects.create_user(username='other', email='other@test.com', password='password123')
        client = Client()
        client.force_login(other_user)
        client.post(f'/accounts/tour-cancel/{booking.id}/')
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'pending')  # Other user cannot cancel!

        client.force_login(self.user)
        client.post(f'/accounts/tour-cancel/{booking.id}/')
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')  # Owner cancels successfully!
