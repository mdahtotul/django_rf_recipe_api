"""
Tests for the user api
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")


def create_user(**params):
    # create and return a new user
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    # test the public features of the user API
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        # test creating a new user with valid payload is successful
        payload = {
            "email": "test@example.com",
            "password": "pass123",
            "name": "Test name",
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_with_email_exists_error(self):
        # test error returned if user wih email exists
        payload = {
            "email": "test@example.com",
            "password": "pass123",
            "name": "Test name",
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        # test error returned if password is too short < 5 characters
        payload = {
            "email": "test@example.com",
            "password": "pass",
            "name": "Test name",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = (
            get_user_model().objects.filter(email=payload["email"]).exists()
        )  # noqa
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        # test generating token for valid credentials
        user_details = {
            "name": "Test Name",
            "email": "test@example.com",
            "password": "pass123",
        }
        create_user(**user_details)

        payload = {
            "email": user_details["email"],
            "password": user_details["password"],
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        # test that token is not generated for invalid credentials
        user_details = {"email": "test@example.com", "password": "goodpass"}
        create_user(**user_details)

        payload = {"email": user_details["email"], "password": "badpass"}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        # test that token is not generated for blank password
        user_details = {"email": "test@example.com", "password": ""}
        create_user(**user_details)

        payload = {"email": user_details["email"], "password": "badpass"}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
