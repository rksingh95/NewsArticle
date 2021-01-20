from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
# Create your views here.
from blog.models import NewsArticle, User
from blog.serializers import NewsArticleListSerializer, NewsArticleCreateSerializer, NewsArticleContentListSerializer, \
    UserListSerializer


class NewsArticleViews(generics.ListCreateAPIView):
    authentication_classes = ()
    permission_classes = ()
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
    authentication_classes = ()
    permission_classes = ()
    queryset = NewsArticle.objects.filter(published=True).order_by('-updated_at')

    def get_serializer_class(self):
        if self.request and self.request.method == 'GET':
            return NewsArticleContentListSerializer


class NewsArticleDetail(generics.RetrieveAPIView):

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
    authentication_classes = ()
    permission_classes = ()
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request and self.request.method == 'GET':
            return UserListSerializer
