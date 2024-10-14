from django.test import TestCase
from .models import Author, Place, Description, User, PlaceDescription

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="TestUser", email="testuser@example.com")

    def test_user_creation(self):
        self.assertEqual(self.user.username, "TestUser")
        self.assertEqual(self.user.email, "testuser@example.com")


class DescriptionModelTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Author1", email="author1@example.com")
        self.description = Description.objects.create(content="Test description", author=self.author)

    def test_description_creation(self):
        self.assertEqual(self.description.content, "Test description")
        self.assertEqual(self.description.author.name, "Author1")

class PlaceDescriptionModelTest(TestCase):
    def setUp(self):
        self.place = Place.objects.create(name="Place1", latitude=59.934280, longitude=30.335098)
        self.author = Author.objects.create(name="Author1", email="author1@example.com")
        self.description = Description.objects.create(content="Description for Place1", author=self.author)
        self.place_description = PlaceDescription.objects.create(place=self.place, description=self.description)

    def test_place_description_creation(self):
        self.assertEqual(self.place_description.place.name, "Place1")
        self.assertEqual(self.place_description.description.content, "Description for Place1")


from django.test import TestCase
from django.contrib.auth.models import User


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='Password123')

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/login.html')

    def test_login_view_post(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'Password123',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        self.assertTrue('_auth_user_id' in self.client.session)

class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='Password123')
        self.client.login(username='testuser', password='Password123')

    def test_logout_view(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        self.assertFalse('_auth_user_id' in self.client.session)


from django.test import TestCase
from .forms import UserRegisterForm

class UserRegisterFormTest(TestCase):


    def test_invalid_email(self):
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password1': 'Pass1234',
            'password2': 'Pass1234'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_passwords_not_matching(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'Pass1234',
            'password2': 'Pass5678'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


from django.test import TestCase
from unittest.mock import patch
from .gpt_utils import generate_description


class GPTUtilsTest(TestCase):
    @patch('openai.ChatCompletion.create')
    def test_generate_description(self, mock_create):
        mock_create.return_value = {
            'choices': [{'message': {'content': 'описание места'}}]
        }

        description = generate_description("Эрмитаж")
        self.assertIn("эрмитаж", description)
        self.assertIn("музей", description)

from django.test import TestCase
from django.urls import reverse
from .models import Place

class GetPOIDescriptionTest(TestCase):
    def setUp(self):
        # Создаем тестовое место
        self.place = Place.objects.create(name='Test Place', latitude=59.934280, longitude=30.335098)

    def test_get_poi_description(self):
        # Выполняем запрос с существующим местом
        response = self.client.post(reverse('get_poi_description'), {
            'place_name': 'Test Place',
            'action': 'get_poi_description'
        })
        self.assertEqual(response.status_code, 200)


from django.test import TestCase
from .models import Place

class PlaceModelTest(TestCase):
    def setUp(self):
        self.place = Place.objects.create(
            name="Hermitage Museum",
            latitude=59.9398,
            longitude=30.3146
        )

    def test_place_creation(self):
        self.assertEqual(self.place.name, "Hermitage Museum")
        self.assertEqual(self.place.latitude, 59.9398)
        self.assertEqual(self.place.longitude, 30.3146)

    def test_place_str_method(self):
        self.assertEqual(str(self.place), "Hermitage Museum")

