from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Experience, Location, Tag
from experience.serializers import ExperienceSerializer, ExperienceDetailSerializer

EXPERIENCE_URL = reverse('experience:experience-list')

def detail_url(experience_id):
    """Return experience detail URL"""
    return reverse('experience:experience-detail', args=[experience_id])

def sample_tag(user, name='Outdoor'):
    """Craete and return a smaple tag"""
    return Tag.objects.create(user=user, name=name)

def sample_location(user, **params):
    """Create a sample location"""
    defaults = {
        'name':'Anchorage Park',
        'description':'Tennis and volleyball'
    }
    defaults.update(params)
    return Location.objects.create(user=user, **defaults)


def sample_experience(user, **params):
    """Create and return a sample experience"""
    defaults = {
        'title': 'Sample Experience',
        'time_minutes': 30,
        'price': 20.00,
        'location': sample_location(user=user)
    }
    defaults.update(params)

    return Experience.objects.create(user=user, **defaults)


class PublicExperienceApiTests(TestCase):
    """Test unauthenticated experience access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(EXPERIENCE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateExperienceApiTests(TestCase):
    """Test authenticated experience API access"""

    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            'test@website.com',
            'testpassword'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_experiences(self):
        """Test retrieving a list of experiences"""
        sample_experience(user=self.user)
        sample_experience(user=self.user)

        res = self.client.get(EXPERIENCE_URL)

        experiences = Experience.objects.all().order_by('-id')
        serializer = ExperienceSerializer(experiences, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_experiences_limited_to_user(self):
        """Test retrieving experiences for user"""
        user2 = get_user_model().objects.create_user(
            'test2@website.com',
            'testpass2'
        )

        sample_experience(user=user2)
        sample_experience(user=self.user)

        res = self.client.get(EXPERIENCE_URL)

        experiences = Experience.objects.filter(user=self.user).order_by('-id')
        serializer = ExperienceSerializer(experiences, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(serializer.data, res.data)
    
    def test_view_experience_detail(self):
        """Test viewing a experience detail"""
        experience = sample_experience(user=self.user)
        experience.tags.add(sample_tag(user=self.user))

        url = detail_url(experience.id)

        res = self.client.get(url)

        serializer = ExperienceDetailSerializer(experience)

        self.assertEqual(serializer.data, res.data)

    def test_create_basic_experience(self):
        """Test creating experiences"""
        samp_loc = sample_location(user=self.user, name='Dyer Park')
        
        payload = {
            'title': 'Workshop',
            'time_minutes': 45,
            'price': '50.00',
            'location': samp_loc.id
        }

        res = self.client.post(EXPERIENCE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        experience = Experience.objects.get(id=res.data['id'])
        serializer = ExperienceSerializer(experience)
        for key in payload.keys():
            self.assertEqual(payload[key], serializer.data[key])
    
    def test_create_experience_with_tags(self):
        """Test creating an experience with tags"""
        tag1 = sample_tag(user=self.user, name='skill')
        tag2 = sample_tag(user=self.user, name='Arts')
        loc1 = sample_location(user=self.user)
        payload = {
            'title': 'Workshop',
            'time_minutes': 45,
            'price': '20.00',
            'location': loc1.id,
            'tags': [tag1.id, tag2.id]
        }

        res = self.client.post(EXPERIENCE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        experience = Experience.objects.get(id=res.data['id'])
        tags = experience.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)
