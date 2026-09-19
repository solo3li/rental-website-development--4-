from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.properties.models import Property
from apps.tours.models import TourBooking

class ToursAppTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tourstudent', email='tour@student.com', password='password123')
        self.user.profile.phone = '01011223344'
        self.user.profile.save()

        self.prop = Property.objects.create(
            title='Sample Cairo Dorm',
            price_egp=2200,
            address='بين السرايات',
            city='الجيزة'
        )

    def test_tour_booking_attaches_authenticated_user(self):
        """Verify book_tour attaches request.user to TourBooking"""
        client = Client()
        client.force_login(self.user)

        response = client.post('/tours/book/?format=json', {
            'property': self.prop.id,
            'full_name': 'طالب تجريبي',
            'email': 'tour@student.com',
            'phone': '01011223344',
            'tour_date': '2026-10-01',
            'tour_type': 'in_person',
            'message': 'أريد المعاينة عصراً',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        booking = TourBooking.objects.filter(email='tour@student.com').first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.property, self.prop)

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
