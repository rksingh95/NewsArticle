from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import views # Explicitly import views for APIView
from django.utils import timezone # For setting unsubscribed_at

# Create your views here.
from blog.models import NewsArticle, User, Subscription # Add Subscription import
from blog.serializers import ( # Organize imports
    NewsArticleListSerializer,
    NewsArticleCreateSerializer,
    NewsArticleContentListSerializer,
    UserListSerializer,
    SubscriptionSerializer # Add SubscriptionSerializer import
)


class NewsArticleViews(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = NewsArticle.objects.filter(published=True).order_by('-updated_at')

    def get_serializer_class(self):
        if self.request and self.request.method == 'GET':
            return NewsArticleListSerializer
        elif self.request and self.request.method == 'POST':
            return NewsArticleCreateSerializer

    def create(self, request, *args, **kwargs):
        """
        Return article ID after creating an article for the requesting user.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'article_id': serializer.instance.id}, status=status.HTTP_201_CREATED)


class NewsArticleContentViews(generics.ListAPIView):
    authentication_classes = () # Assuming public, so no specific auth needed beyond global settings if any
    permission_classes = [AllowAny]
    queryset = NewsArticle.objects.filter(published=True).order_by('-updated_at')

    def get_serializer_class(self):
        if self.request and self.request.method == 'GET':
            return NewsArticleContentListSerializer


class NewsArticleDetail(generics.RetrieveAPIView):
    authentication_classes = () # Assuming public
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        article_id = self.kwargs.get('pk', None)
        article = get_object_or_404(NewsArticle.objects.all(), id=article_id)
        return Response(self.get_response_data(article=article),
                        status=status.HTTP_201_CREATED)

    def get_response_data(self, article):
        return {
            "id": article.id,
            "headline": article.headline,
            "content": article.content,
            "author_email": article.author.email,
            "author_id": article.author.id,
            "category_title": article.category.title,
            "updated_at": article.updated_at
        }


class UserView(generics.ListAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request and self.request.method == 'GET':
            return UserListSerializer


def home(request):
    return render(request, 'home.html')


class SubscriptionView(views.APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Retrieve current user's subscription status."""
        try:
            subscription = Subscription.objects.get(user=request.user)
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response({'status': 'not_subscribed'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        """Subscribe the current user or re-activate existing subscription."""
        subscription, created = Subscription.objects.get_or_create(user=request.user)
        
        if not subscription.is_active:
            subscription.is_active = True
            subscription.unsubscribed_at = None
            # If it's a re-subscription, you might want to update subscribed_at,
            # but typically it remains the original subscription date.
            # For simplicity, we're not changing subscribed_at here on reactivation.
            subscription.save()
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data, status=status.HTTP_200_OK) # Reactivated
        
        serializer = SubscriptionSerializer(subscription)
        if created:
            return Response(serializer.data, status=status.HTTP_201_CREATED) # Newly created and active
        else:
            return Response(serializer.data, status=status.HTTP_200_OK) # Already active

    def delete(self, request, *args, **kwargs):
        """Unsubscribe (deactivate) the current user's subscription."""
        try:
            subscription = Subscription.objects.get(user=request.user, is_active=True)
            subscription.is_active = False
            subscription.unsubscribed_at = timezone.now() # Make sure to import timezone: from django.utils import timezone
            subscription.save()
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Subscription.DoesNotExist:
            return Response({'status': 'not_subscribed_or_already_inactive'}, status=status.HTTP_404_NOT_FOUND)
