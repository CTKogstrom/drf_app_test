from logging import StreamHandler
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Experience, Location, Tag
from experience.serializers import ExperienceSerializer, ExperienceDetailSerializer
import tempfile
import os
from PIL import Image


EXPERIENCE_URL = reverse('experience:experience-list')

def image_upload_url(experience_id):
    """Return URL for experience upload"""
    return reverse('experience:experience-upload-image', args=[experience_id])


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

    def test_partial_update_experience(self):
        """Test updating one field in an experience"""
        experience = sample_experience(user=self.user)
        experience.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Yolo')

        payload = {'title':'Lesson', 'tags':[new_tag.id]}

        url = detail_url(experience.id)
        self.client.patch(url, payload)

        experience.refresh_from_db()

        self.assertEqual(experience.title, payload['title'])
        tags = experience.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertEqual(new_tag, tags[0])

    def test_full_update_experience(self):
        """Test updating an experience with PUT"""
        experience = sample_experience(user=self.user)
        experience.tags.add(sample_tag(user=self.user))
        loc = sample_location(user=self.user)
        payload = {
            'title': 'Lessons',
            'time_minutes': 33,
            'price': '33.00',
            'location': loc.id
        }
        url = detail_url(experience.id)
        self.client.put(url, payload)

        experience.refresh_from_db()

        self.assertEqual(experience.title, payload['title'])
        self.assertEqual(experience.time_minutes, payload['time_minutes'])
        self.assertEqual(str(experience.price), payload['price'])
        self.assertEqual(experience.tags.all().count(), 0)

    def test_filter_experiences_by_tags(self):
        """Test returning experiences with specific tags"""
        experience1 = sample_experience(user=self.user, title='Tennis')
        experience2 = sample_experience(user=self.user, title='Pickleball')
        tag1 = sample_tag(user=self.user, name = 'raquet sport')
        tag2 = sample_tag(user=self.user, name='Active')
        experience1.tags.add(tag1)
        experience2.tags.add(tag2)
        experience3 = sample_experience(user=self.user, title='PingPong')

        res = self.client.get(
            EXPERIENCE_URL,
            {'tags':f'{tag1.id},{tag2.id}'}
        )

        serializer1 = ExperienceSerializer(experience1)
        serializer2 = ExperienceSerializer(experience2)
        serializer3 = ExperienceSerializer(experience3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
    
    def test_filter_recipes_by_location(self):
        """Test returning experiences with specific location"""

        experience1 = sample_experience(user=self.user, title='Tennis', location=sample_location(user=self.user, name='Russo Park'))
        experience2 = sample_experience(user=self.user, title='Pickleball', location=sample_location(user=self.user, name='Dyer Park'))

        experience3 = sample_experience(user=self.user, title='pingpong')

        res = self.client.get(
            EXPERIENCE_URL,
            {'locations':f'{experience1.location.id},{experience2.location.id}'}
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer1 = ExperienceSerializer(experience1)
        serializer2 = ExperienceSerializer(experience2)
        serializer3 = ExperienceSerializer(experience3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
        
        

        


class ExperienceImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@website.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.experience = sample_experience(user=self.user)

    def tearDown(self):
        self.experience.image.delete()

    def test_upload_image_to_experience(self):
        """Test uploading an image to an experience"""
        url = image_upload_url(self.experience.id)
        
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new("RGB", (10,10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image':ntf}, format='multipart')

        self.experience.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.experience.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.experience.id)
        res = self.client.post(url, {'image': 'notanimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)