from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User
from .models import University, MetroStation, Property
from .admin import PropertyAdmin, UniversityAdmin, MetroStationAdmin
from .views import property_list

class PropertyModelAndAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.university = University.objects.create(
            name='Cairo University',
            name_ar='جامعة القاهرة',
            short_code='CU',
            city='الجيزة',
            lat='30.0276',
            lng='31.2089',
            location=Point(31.2089, 30.0276, srid=4326)
        )
        self.metro = MetroStation.objects.create(
            name='Cairo University',
            name_ar='جامعة القاهرة',
            line='line_2',
            lat='30.0282',
            lng='31.2019',
            location=Point(31.2019, 30.0282, srid=4326)
        )
        self.property = Property.objects.create(
            title='Comfortable Student Dorm Bed near CU',
            title_ar='سرير بسكن طلابي هادئ بجوار جامعة القاهرة',
            description='Close to campus, high speed internet and study desk.',
            description_ar='قريب من الجامعة، إنترنت سريع ومكتب مذاكرة.',
            price_egp=2500,
            deposit_egp=1000,
            rental_type='bed',
            gender_policy='male_only',
            university=self.university,
            nearest_metro=self.metro,
            agent_name='مشرف السكن',
            agent_phone='01012345678',
            whatsapp_number='+201012345678',
            lat='30.0276',
            lng='31.2089',
            location=Point(31.2089, 30.0276, srid=4326)
        )

    def test_admin_fieldsets_validity(self):
        """Verify PropertyAdmin initializes without FieldError (agent_phone fix)"""
        ma = PropertyAdmin(Property, self.site)
        form_class = ma.get_form(None)
        self.assertIn('agent_phone', form_class.base_fields)
        self.assertNotIn('phone_number', form_class.base_fields)

    def test_property_save_and_price_sync(self):
        """Verify price synchronizes with price_egp and point geometry syncs with lat/lng"""
        self.assertEqual(self.property.price, 2500)
        self.assertIsNotNone(self.property.location)
        self.assertIn('201012345678', self.property.get_whatsapp_url(is_ar=True))

    def test_property_list_view(self):
        """Verify property_list view renders successfully with filters"""
        factory = RequestFactory()
        request = factory.get('/?gender=male&rental_type=bed')
        request.session = {'lang': 'ar'}
        request.user = User()
        response = property_list(request)
        self.assertEqual(response.status_code, 200)
