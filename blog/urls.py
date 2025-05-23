from django.urls import path

from .views import (
    NewsArticleViews,
    UserView,
    NewsArticleContentViews,
    NewsArticleDetail,
    home,
    SubscriptionView # Import SubscriptionView
)

urlpatterns = [
    path('', home, name='home'), # Added home path for blog app's root
    path("news/articles/", NewsArticleViews.as_view(), name='news-list'),
    path("news/articles/content/", NewsArticleContentViews.as_view(), name='news-content-list'), # Changed name for clarity
    path("news/articles/<uuid:pk>/", NewsArticleDetail.as_view(), name='news-detail'), # Changed name for clarity
    path("users/", UserView.as_view(), name='user-list'), # Changed name for clarity
    path('subscription/', SubscriptionView.as_view(), name='user-subscription'), # Add subscription URL
]
