import google.generativeai as genai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set. AIService will not be able to generate content.")
            self.model = None
            return

        try:
            genai.configure(api_key=self.api_key)
            # Initialize the GenerativeModel. You might want to specify a model name.
            # For example, 'gemini-pro' for text generation.
            self.model = genai.GenerativeModel('gemini-pro') 
            logger.info("AIService initialized successfully with Gemini model.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}", exc_info=True)
            self.model = None

    def generate_newsletter_content(self, topic="Summarize the latest happenings in the AI world for a newsletter."):
        if not self.model:
            logger.error("AIService cannot generate content because the Gemini model is not initialized (API key missing or initialization failed).")
            return "Error: AI Service not available."

        try:
            # Example prompt. You might want to make this more dynamic.
            prompt = f"""
            As an AI assistant for a newsletter, please generate a concise and engaging summary
            about the following topic: '{topic}'. The summary should be suitable for a general audience
            interested in AI. Keep it under 200 words.
            """
            
            response = self.model.generate_content(prompt)
            
            # Accessing the text content depends on the response structure of the Gemini API.
            # This is a common way, but might need adjustment based on the actual API response object.
            if hasattr(response, 'text') and response.text:
                return response.text
            elif hasattr(response, 'parts'): # More robust check for Gemini's newer API
                all_text = "".join(part.text for part in response.parts if hasattr(part, 'text'))
                if all_text:
                    return all_text
            
            logger.warning(f"Gemini API response did not contain expected text content. Response: {response}")
            return "Error: Could not extract content from AI response."

        except Exception as e:
            logger.error(f"Error generating content with Gemini: {e}", exc_info=True)
            return f"Error: AI content generation failed. Details: {str(e)}"

# Example usage (optional, for testing the service directly if needed):
# if __name__ == '__main__':
#     # This part would only run if you execute this file directly,
#     # and Django settings need to be configured (e.g., by calling django.setup()).
#     # For now, this is commented out as service will be used via Django.
#     # import django
#     # import os # Make sure os is imported if using os.environ
#     # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsArticle.settings')
#     # django.setup()
#     #
#     # if settings.GEMINI_API_KEY:
#     #     service = AIService()
#     #     content = service.generate_newsletter_content("The future of generative AI models.")
#     #     print(content)
#     # else:
#     #     print("Skipping AIService example usage as GEMINI_API_KEY is not set.")
