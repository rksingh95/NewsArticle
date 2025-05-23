from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status # For HTTP status codes
from .models import Subscription # Add this
from django.utils import timezone # Add this
from unittest.mock import patch, MagicMock # For mocking the Gemini API
from django.conf import settings # To manipulate settings for testing
from blog.services import AIService # Import the service
# import json # Not explicitly used in provided tests, but good for raw response debugging

# Direct import check for allauth.account.middleware
try:
    import allauth.account.middleware
    print("Successfully imported allauth.account.middleware in tests.py")
except ModuleNotFoundError as e:
    print(f"Failed to import allauth.account.middleware in tests.py: {e}")

User = get_user_model() # To create a test user

# Create your tests here.
class HomePageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('home') # Assuming 'home' is the name of your home page URL

    def test_google_login_link_for_anonymous_user(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login with Google")
        self.assertNotContains(response, "Logout")

    def test_logout_link_for_authenticated_user(self):
        # Create a test user
        # Provide email as username since USERNAME_FIELD = 'email'
        test_user = User.objects.create_user(username='testuser@example.com', email='testuser@example.com', password='password123', first_name='Test', last_name='User')
        self.client.login(email='testuser@example.com', password='password123')
        
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Logout")
        self.assertNotContains(response, "Login with Google")
        
        # Clean up user (optional, as test DB is usually torn down)
        test_user.delete()


class SubscriptionTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Provide email as username since USERNAME_FIELD = 'email'
        self.user = User.objects.create_user(username='subtest@example.com', email='subtest@example.com', password='password123', first_name='Sub', last_name='Scriber')
        self.subscription_url = reverse('user-subscription')

        # Log in the user for most tests
        self.client.login(email='subtest@example.com', password='password123')

    def test_subscribe_user(self):
        response = self.client.post(self.subscription_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertTrue(data['is_active'])
        self.assertTrue(Subscription.objects.filter(user=self.user, is_active=True).exists())

    def test_get_subscription_status_active(self):
        Subscription.objects.create(user=self.user, is_active=True)
        response = self.client.get(self.subscription_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['is_active'])

    def test_get_subscription_status_inactive(self):
        Subscription.objects.create(user=self.user, is_active=False, unsubscribed_at=timezone.now())
        response = self.client.get(self.subscription_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK) # Still 200 OK, but is_active is false
        data = response.json()
        self.assertFalse(data['is_active'])
        self.assertIsNotNone(data['unsubscribed_at'])
        
    def test_get_subscription_status_not_subscribed(self):
        # Ensure no subscription exists for this user
        Subscription.objects.filter(user=self.user).delete()
        response = self.client.get(self.subscription_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unsubscribe_user(self):
        # First, subscribe the user
        Subscription.objects.create(user=self.user, is_active=True)
        
        response = self.client.delete(self.subscription_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertFalse(data['is_active'])
        self.assertIsNotNone(data['unsubscribed_at'])
        self.assertTrue(Subscription.objects.filter(user=self.user, is_active=False).exists())

    def test_unsubscribe_user_not_active_or_not_subscribed(self):
        # Case 1: No subscription
        Subscription.objects.filter(user=self.user).delete()
        response = self.client.delete(self.subscription_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Case 2: Already inactive
        Subscription.objects.create(user=self.user, is_active=False, unsubscribed_at=timezone.now())
        response = self.client.delete(self.subscription_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscribe_when_already_active(self):
        Subscription.objects.create(user=self.user, is_active=True)
        response = self.client.post(self.subscription_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK) # Not 201, as it's not newly created
        data = response.json()
        self.assertTrue(data['is_active'])

    def test_reactivate_subscription(self):
        sub = Subscription.objects.create(user=self.user, is_active=False, unsubscribed_at=timezone.now())
        response = self.client.post(self.subscription_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK) # Reactivated
        data = response.json()
        self.assertTrue(data['is_active'])
        self.assertIsNone(data['unsubscribed_at']) # Check if unsubscribed_at is cleared
        sub.refresh_from_db()
        self.assertTrue(sub.is_active)
        self.assertIsNone(sub.unsubscribed_at)

    def test_subscription_endpoints_unauthenticated(self):
        self.client.logout() # Ensure user is logged out
        
        response_get = self.client.get(self.subscription_url)
        # DRF's default for IsAuthenticated without specific unauth handler is 401
        # However, allauth might change this to 403 if SessionAuth is primary and no CSRF
        # Let's stick to 401 for now as it's a common DRF behavior with TokenAuth also in play.
        self.assertIn(response_get.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]) 
        
        response_post = self.client.post(self.subscription_url)
        self.assertIn(response_post.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        
        response_delete = self.client.delete(self.subscription_url)
        self.assertIn(response_delete.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class AIServiceTests(TestCase):
    @patch('blog.services.genai.GenerativeModel') # Mock the model initialization
    @patch('blog.services.genai.configure') # Mock configure
    def test_aiservice_initialization_success(self, mock_configure, mock_generative_model):
        # Temporarily set API key for this test
        with self.settings(GEMINI_API_KEY='fake_test_key'):
            service = AIService()
            self.assertIsNotNone(service.model)
            mock_configure.assert_called_once_with(api_key='fake_test_key')
            mock_generative_model.assert_called_once_with('gemini-pro')

    def test_aiservice_initialization_no_api_key(self):
        with self.settings(GEMINI_API_KEY=None):
            service = AIService()
            self.assertIsNone(service.model)
            # Check logs or a specific state if your service sets one for no key

    @patch('blog.services.genai.GenerativeModel')
    @patch('blog.services.genai.configure')
    def test_generate_content_success(self, mock_configure, mock_generative_model_class):
        # Configure the mock model instance returned by GenerativeModel()
        mock_model_instance = MagicMock()
            
        # Configure the mock object that self.model.generate_content() will return
        mock_response = MagicMock()
        mock_response.text = None # Explicitly make .text false-y or non-existent for this test path
            
        mock_part = MagicMock()
        mock_part.text = "Generated AI content from parts."
        mock_response.parts = [mock_part]
            
        mock_model_instance.generate_content.return_value = mock_response
        mock_generative_model_class.return_value = mock_model_instance

        with self.settings(GEMINI_API_KEY='fake_test_key'):
            service = AIService()
            self.assertIsNotNone(service.model, "Model should be initialized for this test")
            
            topic = "Test Topic"
            # The prompt is assembled inside the method, so we can't directly compare it here
            # without replicating the logic. Instead, we'll check that the mock was called
            # and that the topic is part of the prompt.
            content = service.generate_newsletter_content(topic=topic)
            
            # Check that generate_content was called with a prompt containing the topic
            args, _ = mock_model_instance.generate_content.call_args
            self.assertIn(topic, args[0]) # Check if topic is in the first argument (prompt)
            self.assertEqual(content, "Generated AI content from parts.")


    @patch('blog.services.genai.GenerativeModel')
    @patch('blog.services.genai.configure')
    def test_generate_content_api_error(self, mock_configure, mock_generative_model_class):
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.side_effect = Exception("Gemini API Error")
        mock_generative_model_class.return_value = mock_model_instance

        with self.settings(GEMINI_API_KEY='fake_test_key'):
            service = AIService()
            self.assertIsNotNone(service.model)
            content = service.generate_newsletter_content(topic="Error Topic")
            self.assertTrue(content.startswith("Error: AI content generation failed."))
            self.assertIn("Gemini API Error", content)

    def test_generate_content_no_api_key(self):
        with self.settings(GEMINI_API_KEY=None):
            service = AIService()
            self.assertIsNone(service.model)
            content = service.generate_newsletter_content(topic="No Key Topic")
            self.assertEqual(content, "Error: AI Service not available.")
