from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.accounts.forms import StudentRegisterForm, LandlordRegisterForm
from apps.accounts.models import UserProfile
from apps.properties.models import Property

class AccountsAppTests(TestCase):
    def test_student_registration_form_django_51_compatibility(self):
        """Ensure StudentRegisterForm creates user without make_random_password AttributeError"""
        form_data = {
            'first_name': 'أحمد',
            'last_name': 'محمود',
            'email': 'ahmed.student@example.com',
            'password': 'SecurePassword123!',
            'gender': 'male',
            'phone': '01012345678',
            'faculty': 'هندسة القاهرة',
            'academic_year': 'الفرقة الثالثة',
        }
        form = StudentRegisterForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertIsNotNone(user.pk)
        self.assertTrue(user.username.startswith('ahmed.student_'))
        self.assertEqual(user.profile.user_type, 'student')
        self.assertEqual(user.profile.gender, 'male')

    def test_landlord_registration_form_django_51_compatibility(self):
        """Ensure LandlordRegisterForm creates user without make_random_password AttributeError"""
        form_data = {
            'first_name': 'عماد',
            'last_name': 'عثمان',
            'email': 'emad.landlord@example.com',
            'password': 'SecurePassword123!',
            'phone': '01198765432',
            'whatsapp': '01198765432',
            'company_name': 'سكن الدقي الجامعي',
            'bio': 'إدارة سكن طالبات وطلاب بالدقي',
        }
        form = LandlordRegisterForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertIsNotNone(user.pk)
        self.assertTrue(user.username.startswith('emad.landlord_'))
        self.assertEqual(user.profile.user_type, 'landlord')
        self.assertEqual(user.profile.company_name, 'سكن الدقي الجامعي')

    def test_user_login_view(self):
        """Test authentication via email"""
        user = User.objects.create_user(username='teststudent', email='student@test.com', password='TestPassword123!')
        client = Client()
        response = client.post('/accounts/login/', {
            'email': 'student@test.com',
            'password': 'TestPassword123!',
        })
        self.assertEqual(response.status_code, 302)

    def test_update_beds_view_authorization(self):
        """Test that unauthorized users cannot update beds"""
        landlord = User.objects.create_user(username='owner1', email='owner@test.com', password='password123')
        landlord.profile.user_type = 'landlord'
        landlord.profile.phone = '01000000001'
        landlord.profile.save()

        hacker = User.objects.create_user(username='hacker', email='hacker@test.com', password='password123')
        hacker.profile.user_type = 'student'
        hacker.profile.phone = '01000000002'
        hacker.profile.save()

        prop = Property.objects.create(
            title='Test Property',
            owner=landlord,
            agent_phone='01000000001',
            total_capacity=4,
            available_beds=2,
            price_egp=2000
        )

        client = Client()
        client.force_login(hacker)
        response = client.post(f'/accounts/dashboard/update-beds/{prop.id}/', {'delta': 1})
        prop.refresh_from_db()
        self.assertEqual(prop.available_beds, 2)  # Beds must not change!

        client.force_login(landlord)
        response = client.post(f'/accounts/dashboard/update-beds/{prop.id}/', {'delta': 1})
        prop.refresh_from_db()
        self.assertEqual(prop.available_beds, 3)  # Beds incremented by authorized owner!
