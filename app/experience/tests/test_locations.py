from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Location
from experience.serializers import LocationSerializer

LOCATIONS_URL = reverse('experience:location-list')

class PublicLocationsApiTests(TestCase):
    """Test the publicly available locations API"""

    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        """Test that login is required to access to the endpoint"""

        res = self.client.get(LOCATIONS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateLocationsApiTests(TestCase):
    """Test the private locations api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@website.com',
            'testpassword'
        )

        self.client.force_authenticate(self.user)
    
    def test_retrieve_locations_list(self):
        """Test retrieving a list of locations"""
        Location.objects.create(user=self.user, name='Dyer Park', description='Park on the beline highway')
        Location.objects.create(user=self.user, name='Anchorage Park', description='Park in the heart of North Palm Beach')

        res = self.client.get(LOCATIONS_URL)

        locations = Location.objects.all().order_by('-name')
        serializer = LocationSerializer(locations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_locations_limited_to_user(self):
        """Test that locations for the authenticated user are returned"""

        user2 = get_user_model().objects.create_user(
            'user2@website.com',
            'testpassword2'
        )

        Location.objects.create(user=self.user, name='Dyer Park', description='Park on the beline highway')
        Location.objects.create(user=self.user, name='Russo Park', description='New Soccer and Tennis Complex in Palm Beach Gardens')
        Location.objects.create(user=user2, name='Anchorage Park', description='Park in the heart of North Palm Beach')

        locations = Location.objects.filter(user=self.user).order_by('-name')
        serializer = LocationSerializer(locations, many=True)

        res = self.client.get(LOCATIONS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_location_successful(self):
        """Test create a new ingredient"""

        payload = {
            'name': 'Anchorage Park',
            'description': 'Park with tennis and volleyball courts'
        }

        self.client.post(LOCATIONS_URL, payload)

        exists = Location.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_location_invalid(self):
        """Test create an invalid location fails"""

        payload = {
            'name': ''
        }

        res = self.client.post(LOCATIONS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
