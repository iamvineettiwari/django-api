from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')

def create_user(**params) :
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """Test the users API public"""

    def setUp(self):
        self.client = APIClient()
    
    def test_create_valid_user_successfull(self):
        """Test creating user with value payload is successfull"""
        payload = {
            "email": "test@test.com",
            "password": "12345",
            "name": "Jhon Doe"
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user  = get_user_model().objects.get(**res.data)
        self.assertFalse(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)
    
    def test_user_exists(self):
        """Test creating user that already exists fails"""
        payload = {
            "email": "test@test.com",
            "password": "12345"
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_too_short(self):
        """Test that the password is having more than 5 characters"""
        payload = {
            "email": "test@test.com",
            "password": "ab"
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(email = payload.get("email")).exists()

        self.assertFalse(user_exists)
    
    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            "email": "test@test.com",
            "password": "test@123",
            "name": "Jhon Doe"
        }

        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("token", res.data)
    
    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credential is provided"""
        create_user(email='test@test.com', password='test@123', name='Jhon Doe')

        payload = {
            "email": "test@test.com",
            "password": "123"
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)
    
    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exists"""

        payload = {
            "email": "test@test.com",
            "password": "123"
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)
    
    def test_create_token_missing_fields(self):
        """Test that email and password are required"""

        res = self.client.post(TOKEN_URL, {
            'email': 'test',
            'password': ''
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)