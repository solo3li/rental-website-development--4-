from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.roommates.models import RoommatePost

class RoommatesAppTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='roommatestudent', email='roommate@test.com', password='password123')
        self.student.profile.gender = 'female'
        self.student.profile.phone = '01234567890'
        self.student.profile.save()

    def test_roommate_post_submission_attaches_user(self):
        """Verify roommate post attaches authenticated user"""
        client = Client()
        client.force_login(self.student)

        response = client.post('/roommates/', {
            'student_name': 'سارة أحمد',
            'gender': 'female',
            'faculty': 'طب قصر العيني',
            'academic_year': 'الفرقة الرابعة',
            'target_area': 'المنيل / الجيزة',
            'budget_max_egp': 3000,
            'move_in_date': 'أول الشهر القادم',
            'sleep_habit': 'استذكار مسائي هادئ',
            'bio': 'أبحث عن زميلة سكن هادئة ومرتبة',
            'contact_phone': '01234567890',
            'whatsapp_number': '01234567890',
        })
        self.assertEqual(response.status_code, 302)

        post = RoommatePost.objects.filter(student_name='سارة أحمد').first()
        self.assertIsNotNone(post)
        self.assertEqual(post.user, self.student)
        self.assertEqual(post.budget_max_egp, 3000)
        self.assertTrue(post.is_active)

    def test_roommate_toggle_and_delete_authorization(self):
        """Verify student can toggle and delete their own roommate post, while others are denied"""
        post = RoommatePost.objects.create(
            user=self.student,
            student_name='سارة أحمد',
            gender='female',
            faculty='طب قصر العيني',
            target_area='المنيل',
            budget_max_egp=3000,
            contact_phone='01234567890',
            whatsapp_number='01234567890',
            is_active=True
        )

        intruder = User.objects.create_user(username='intruder', email='intruder@test.com', password='password123')
        client = Client()
        client.force_login(intruder)
        client.post(f'/accounts/roommate-toggle/{post.id}/')
        post.refresh_from_db()
        self.assertTrue(post.is_active)  # Intruder cannot toggle!

        client.force_login(self.student)
        client.post(f'/accounts/roommate-toggle/{post.id}/')
        post.refresh_from_db()
        self.assertFalse(post.is_active)  # Owner successfully toggled to inactive!

        client.force_login(self.student)
        client.post(f'/accounts/roommate-delete/{post.id}/')
        self.assertFalse(RoommatePost.objects.filter(id=post.id).exists())  # Owner deleted post!
