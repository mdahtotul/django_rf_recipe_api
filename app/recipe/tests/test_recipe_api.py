"""
  Test for recipe APIs
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe, Tag

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    # return recipe detail URL
    return reverse("recipe:recipe-detail", args=[recipe_id])


def create_recipe(user, **params):
    # create and return a sample recipe
    defaults = {
        "title": "Sample recipe title",
        "time_minutes": 10,
        "price": Decimal("5.25"),
        "description": "Sample description",
        "link": "http://example.com/recipe.pdf",
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    # create and return a sample user
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
    # test unauthenticated recipe API access
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        # test that authentication is required
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    # test authenticated recipe API access
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="test@example.com",
            password="pass123",
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self):
        # test retrieving a list of recipes
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by("-id")
        serializers = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializers.data)

    def test_recipes_limited_to_user(self):
        # test retrieving recipes for user
        user2 = create_user(
            email="test2@example.com",
            password="pass123",
        )
        create_recipe(user=user2)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializers = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializers.data)

    def test_get_recipe_detail(self):
        # test viewing a recipe detail
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        # test creating a new recipe
        payload = {
            "title": "Sample recipe title",
            "time_minutes": 10,
            "price": Decimal("5.25"),
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        # test updating a recipe with patch
        original_link = "https://example.com/recipe.pdf"
        recipe = create_recipe(
            title="Simple recipe title",
            user=self.user,
            link=original_link,
        )

        payload = {"title": "New recipe title"}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update_recipe(self):
        # test full update of recipe
        recipe = create_recipe(
            title="Simple recipe title",
            user=self.user,
            link="https://example.com/recipe.pdf",
            description="Sample description",
        )

        payload = {
            "title": "New recipe title",
            "link": "https://example.com/new_recipe.pdf",
            "time_minutes": 15,
            "price": Decimal("10.50"),
            "description": "New description",
        }

        url = detail_url(recipe.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        # test that user can't update another user's recipe
        user2 = create_user(
            email="test2@example.com",
            password="pass123",
        )
        recipe = create_recipe(user=self.user)
        payload = {"user": user2.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        # test deleting a recipe
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_errors(self):
        # test that user can't delete another user's recipe
        user2 = create_user(
            email="test2@example.com",
            password="pass123",
        )
        recipe = create_recipe(user=user2)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        # test creating a recipe with tags
        payload = {
            "title": "Recipe with tags",
            "tags": [{"name": "Thai"}, {"name": "Indian"}],
            "time_minutes": 10,
            "price": Decimal("5.00"),
        }
        res = self.client.post(RECIPE_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload["tags"]:
            exists = recipe.tags.filter(
                name=tag["name"],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        # test creating a recipe with existing tags
        tag1 = Tag.objects.create(user=self.user, name="Indian")
        payload = {
            "title": "Panir",
            "tags": [{"name": "Thai"}, {"name": "Indian"}],
            "time_minutes": 10,
            "price": 5.00,
        }
        res = self.client.post(RECIPE_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag1, recipe.tags.all())

        for tag in payload["tags"]:
            exists = recipe.tags.filter(
                name=tag["name"],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        # test updating a recipe with new tags
        recipe = create_recipe(user=self.user)

        payload = {"tags": [{"name": "Lunch"}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name="Lunch")
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        # test updating a recipe with new tags
        recipe = create_recipe(user=self.user)
        tag_lunch = Tag.objects.create(user=self.user, name="Lunch")
        recipe.tags.add(tag_lunch)

        tag_dinner = Tag.objects.create(user=self.user, name="Dinner")
        payload = {"tags": [{"name": "Dinner"}]}

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_dinner, recipe.tags.all())
        self.assertNotIn(tag_lunch, recipe.tags.all())

    def test_clear_recipe_tags(self):
        #  test remove recipe tags
        tag = Tag.objects.create(user=self.user, name="Lunch")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {"tags": []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredients(self):
        # test creating a recipe with ingredients
        payload = {
            "title": "Cauliflower Tacos",
            "time_minutes": 10,
            "price": Decimal("5.00"),
            "ingredients": [
                {"name": "Cauliflower"},
                {"name": "Salt"},
            ],
        }
        res = self.client.post(RECIPE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name=ingredient["name"],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self):
        ingredient = Ingredient.objects.create(user=self.user, name="Salt")

        payload = {
            "title": "Thai Soup",
            "time_minutes": 4,
            "price": Decimal("5.00"),
            "ingredients": [
                {"name": "Chicken"},
                {"name": "Salt"},
            ],
        }
        res = self.client.post(RECIPE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())

        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                user=self.user, name=ingredient["name"]
            ).exists()
            self.assertTrue(exists)
