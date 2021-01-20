from django.urls import path

from .views import NewsArticleViews, UserView, NewsArticleContentViews, NewsArticleDetail

urlpatterns = [
    path("news/articles/", NewsArticleViews.as_view(), name='news-list'),
    path("news/articles/content/", NewsArticleContentViews.as_view(), name='news-list'),
    path("news/articles/<uuid:pk>/", NewsArticleDetail.as_view(), name='news-list-detail'),
    path("users/", UserView.as_view(), name='user'),

]
