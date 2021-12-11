from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from unittest.mock import patch

from core import models

def sample_user(email="test@test.com", password="test"):
    """Create a sample user"""
    return get_user_model().objects.create(**{
        'email': email, 
        'password': password
        })

class ModelTests(TestCase) :

    def test_create_user_with_email_successful(self) :
        """ Test create a new user with an email is successfull"""

        email = "test@test.com"
        password = "12345"

        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)

        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""

        email = "test@Test.COM"
        user = get_user_model().objects.create_user(email, 'test124')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""

        user = get_user_model().objects.create_superuser('test@test.com', 'test123')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
    
    def test_tag_str(self):
        """Test tag string representation"""
        tag = models.Tag.objects.create(**{
            "user": sample_user(),
            "name":'Vegan'}
        )

        self.assertEqual(str(tag), tag.name)
    
    def test_ingredient_str(self):
        """Test the ingredient string representation"""

        ingredient = models.Ingredient.objects.create(**{
            "user":  sample_user(),
            "name": "Cucumber"
        })

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipie_str(self):
        "Test the recipe string representation"

        recipie = models.Recipe.objects.create(**{
            "user": sample_user(),
            "title": "Steak and mushroom sauce",
            "time_minutes": 5,
            "price": 5.00
        })

        self.assertEqual(str(recipie), recipie.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpeg')
        expected_path = f'uploads/recipe/{uuid}.jpeg'
        self.assertEqual(file_path, expected_path)