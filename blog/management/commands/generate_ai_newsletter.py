from django.core.management.base import BaseCommand
from blog.services import AIService # Import your AIService
from django.conf import settings # To check if API key is set

class Command(BaseCommand):
    help = 'Generates newsletter content using the Gemini AI service.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--topic',
            type=str,
            help='Specify a topic for the newsletter content generation.',
            default='The latest advancements in AI and machine learning.' # Default topic
        )

    def handle(self, *args, **options):
        if not settings.GEMINI_API_KEY:
            self.stdout.write(self.style.WARNING('GEMINI_API_KEY is not set. Cannot generate AI newsletter content.'))
            return

        topic = options['topic']
        
        self.stdout.write(self.style.HTTP_INFO(f"Attempting to generate newsletter content for topic: '{topic}'..."))
        
        ai_service = AIService()
        
        # Check if the model was initialized in AIService
        if not ai_service.model:
            self.stdout.write(self.style.ERROR('AIService model not initialized. Check API key and service logs.'))
            return

        content = ai_service.generate_newsletter_content(topic=topic)
        
        if content.startswith("Error:"):
            self.stdout.write(self.style.ERROR(f"Failed to generate content: {content}"))
        else:
            self.stdout.write(self.style.SUCCESS('Successfully generated newsletter content:'))
            self.stdout.write(content)
            # In a real application, you might save this content to a database model here.
