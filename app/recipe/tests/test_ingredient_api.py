from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')

class PublicIngredeitnTests(TestCase):
    """Test the publicly available ingredients api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientTests(TestCase):
    """Test ingredient can be retrieved by authorized user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(**{
            "email": "test@test.com",
            "password": "password"
        })
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(**{
            "user": self.user,
            "name": "Salt"
        })
        Ingredient.objects.create(**{
            "user": self.user,
            "name": "Suger"
        })

        res = self.client.get(INGREDIENT_URL)

        ingredient = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredient, many=True)

        self.assertTrue(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that only ingredient for the authenticated users is returned"""

        user2 = get_user_model().objects.create(**{
            "email": "test34@test.test",
            "password": "test"
        })
        Ingredient.objects.create(**{   
            "user": user2,
            "name": "Salt"
        })
        ingredient = Ingredient.objects.create(**{
            "user": self.user,
            "name": "Suger"
        })

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

        self.assertEqual(res.data[0].get("name"), ingredient.name)
    
    def test_create_ingredient_successful(self):
        """Test create a new ingredient"""

        payload = {
            "name": "cabbage"
        }

        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user = self.user,
            name = payload.get("name")
        ).exists()

        self.assertTrue(exists)
    
    def test_create_ingredient_invalid(self):
        """Test creating invalid ingredient fails"""

        payload = {
            "name": ""
        }

        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipies(self):
        """Test filtering ingredients by those assigned to recipes"""

        ing1 = Ingredient.objects.create(**{
            "user": self.user,
            "name": "Turkey"
        })
        
        ing2 = Ingredient.objects.create(**{
            "user": self.user,
            "name": "Apples"
        })

        recipe = Recipe.objects.create(**{
            "title": "Apple crumble",
            "time_minutes": 5,
            "price":10.00,
            "user": self.user
        })
        recipe.ingredients.add(ing1)
        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ing1)
        serializer2 = IngredientSerializer(ing2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items"""
        ing = Ingredient.objects.create(**{
            "user": self.user,
            "name": "Turkey"
        })
        
        Ingredient.objects.create(**{
            "user": self.user,
            "name": "Apples"
        })

        recipe1 = Recipe.objects.create(**{
            "title": "Apple crumble",
            "time_minutes": 5,
            "price":10.00,
            "user": self.user
        })
        recipe1.ingredients.add(ing)

        recipe2 = Recipe.objects.create(**{
            "title": "Some crumble",
            "time_minutes": 5,
            "price":10.00,
            "user": self.user
        })
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)

