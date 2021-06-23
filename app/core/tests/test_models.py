from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from unittest.mock import patch


def sample_user(email='test@website.com', password='testpass'):
    """Create Sample User"""
    return get_user_model().objects.create_user(email, password)
class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""

        email = 'test@website.com'
        password = 'testpass123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """ Test the new email for a new user is normalized"""

        email = 'test@WEBSITE.COM'
        user = get_user_model().objects.create_user(email, 'test122')

        self.assertEqual(user.email, email.lower()) 
    
    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_super_user(self):
        """Test creating a new superuser"""

        user = get_user_model().objects.create_superuser(
            'test@website.com',
            'test123'
        )
        
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""

        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Sports'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """TEst the ingredient string representation"""
        location = models.Location.objects.create(
            user = sample_user(),
            name='Dyer Park'
        )

        self.assertEqual(str(location), location.name)

    def test_experience_str(self):
        """Test the experience string representation"""
        user = sample_user()
        
        experience = models.Experience.objects.create(
            user = user,
            title = 'Tennis Lessons',
            time_minutes = 2,
            location = models.Location.objects.create(user=user, name='Online'),
            price = 0
        )

        self.assertEqual(str(experience), experience.title)
    
    @patch('uuid.uuid4')
    def test_experience_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid='test-uuid'

        mock_uuid.return_value = uuid
        file_path = models.experience_image_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/experience/{uuid}.jpg'

        self.assertEqual(file_path,exp_path)

