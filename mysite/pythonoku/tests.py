from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Schedule, UserProfile
from .serializers import ScheduleSerializer


class AuthFlowTests(APITestCase):
    def test_register_accepts_username_with_spaces(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'Кадыров Эржан',
            'email': 'erzhan@example.com',
            'password': 'Demo12345!',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(UserProfile.objects.filter(username='Кадыров Эржан').exists())
        self.assertIn('access', response.data)

    def test_login_accepts_email_or_username(self):
        UserProfile.objects.create_user(
            username='Мирбек Окуучу',
            email='mirbek@example.com',
            password='Demo12345!',
        )

        email_response = self.client.post('/api/auth/login/', {
            'username': 'mirbek@example.com',
            'password': 'Demo12345!',
        }, format='json')
        username_response = self.client.post('/api/auth/login/', {
            'username': 'Мирбек Окуучу',
            'password': 'Demo12345!',
        }, format='json')

        self.assertEqual(email_response.status_code, 200)
        self.assertEqual(username_response.status_code, 200)
        self.assertIn('access', email_response.data)
        self.assertIn('access', username_response.data)


class ScheduleSerializerTests(TestCase):
    def test_schedule_exposes_google_meet_alias(self):
        schedule = Schedule.objects.create(
            title='Google Meet урок',
            description='Онлайн-разбор',
            zoom_url='https://meet.google.com/abc-defg-hij',
            date=timezone.now(),
            duration_minutes=60,
        )

        data = ScheduleSerializer(schedule).data

        self.assertEqual(data['meet_url'], 'https://meet.google.com/abc-defg-hij')
