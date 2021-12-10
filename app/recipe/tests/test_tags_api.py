from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, client

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(**{
            "email": "test@test.com",
            "password": "password"
        })

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(**{
            "user": self.user,
            "name": "Vegan"
        })
        Tag.objects.create(**{
            "user": self.user,
            "name": "Desert"
        })
        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')

        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_tag_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""

        user2 = get_user_model().objects.create_user(**{
            "email": "test2@test.com",
            "password": "password"
        })
        
        Tag.objects.create(**{
            "user": user2,
            "name": "Vegan"
        })
        tag = Tag.objects.create(**{
            "user": self.user,
            "name": "Desert"
        })

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0].get("name"), tag.name)

    def test_create_tag_successfull(self):
        """Test creating a new tag"""

        payload = {"name": "Test Tag"}

        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user = self.user,
            name = payload.get("name")
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {"name": ""}
        res = self.client.post(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    