from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


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
