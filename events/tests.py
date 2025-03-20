from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from events.models import User, Location


class UserRegistrationAPITestCase(TestCase):
    def setUp(self):
        # Create a test client
        self.client = APIClient()

        # Create a test location that already exists
        self.existing_location = Location.objects.create(
            name="Existing City",
            latitude=35.6895,
            longitude=139.6917,
            address="Existing City, Country"
        )

    def test_user_registration_success(self):
        """Test successful user registration with new location"""
        url = reverse('user-register')
        data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "location": {
                "name": "New City",  # Different from existing locations
                "latitude": 51.5074,
                "longitude": -0.1278,
                "address": "New City, Country"
            },
            "preferences": {},
            "role": "user"
        }

        response = self.client.post(url, data, format='json')

        # Assert response status code is 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert user was created
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

        # Assert location was created
        self.assertTrue(Location.objects.filter(name="New City").exists())

        # Check the count (should now be 3: Existing City, New City, Another New City)
        self.assertEqual(Location.objects.count(), 2)

    def test_user_registration_with_existing_location(self):
        """Test user registration with an existing location"""
        url = reverse('user-register')
        data = {
            "email": "anotheruser@example.com",
            "password": "securepassword123",
            "location": {
                "name": "Existing City",  # This location already exists
                "latitude": 40.7128,  # Different coordinates
                "longitude": -74.0060,
                "address": "Updated Address"
            },
            "preferences": {},
            "role": "user"
        }

        # Check the count before the test (should be 2 from setUp)
        self.assertEqual(Location.objects.count(), 1)

        response = self.client.post(url, data, format='json')

        # Assert response status code is 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert user was created
        self.assertTrue(User.objects.filter(email="anotheruser@example.com").exists())

        # Assert location was updated
        updated_location = Location.objects.get(name="Existing City")
        self.assertEqual(updated_location.latitude, 40.7128)
        self.assertEqual(updated_location.longitude, -74.0060)
        self.assertEqual(updated_location.address, "Updated Address")

        # Assert the total count of locations is still 2 (the count shouldn't change)
        self.assertEqual(Location.objects.count(), 1)