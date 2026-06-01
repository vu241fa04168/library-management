from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group

class LoginRestrictionTests(TestCase):
    def setUp(self):
        # Ensure the Publisher group exists
        self.publisher_group, _ = Group.objects.get_or_create(name='Publisher')
        
        # Create standard student user
        self.student = User.objects.create_user(username='student1', password='password123', email='student@test.com')
        
        # Create publisher user
        self.publisher = User.objects.create_user(username='publisher1', password='password123', email='publisher@test.com')
        self.publisher.groups.add(self.publisher_group)

        # Create admin user
        self.admin = User.objects.create_superuser(username='admin1', password='password123', email='admin@test.com')

    def test_student_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'student1',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('home'))
        
    def test_publisher_login_denied_on_student_portal(self):
        response = self.client.post(reverse('login'), {
            'username': 'publisher1',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200) # Form is returned with errors
        self.assertContains(response, "Access denied. This login portal is restricted to students only.")

    def test_admin_login_allowed_on_student_portal(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin1',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('home'))

    def test_authenticated_publisher_redirected_from_login(self):
        self.client.login(username='publisher1', password='password123')
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('publisher_dashboard'))

    def test_authenticated_publisher_redirected_from_home(self):
        self.client.login(username='publisher1', password='password123')
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('publisher_dashboard'))

