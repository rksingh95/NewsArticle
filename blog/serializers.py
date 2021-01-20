from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from blog.models import User, NewsArticle, Category


class NewsArticleContentListSerializer(serializers.ModelSerializer):
    author_email = serializers.SerializerMethodField('get_author_email')
    author_id = serializers.SerializerMethodField('get_author_id')
    categories = serializers.SerializerMethodField('get_category')

    class Meta:
        model = NewsArticle
        fields = ('id', 'headline', 'content', 'author_email', 'author_id', 'categories', 'updated_at')
        read_only = ('id', 'headline')

    @staticmethod
    def get_author_email(obj: NewsArticle) -> str:
        return obj.author.email

    @staticmethod
    def get_author_id(obj: NewsArticle) -> str:
        return obj.author.id

    @staticmethod
    def get_category(obj: NewsArticle):
        return obj.category.title


class NewsArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = ('id', 'headline',)
        read_only = ('id', 'headline')


class NewsArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = ('headline', 'content', 'author_id', 'published')

    def create(self, validated_data: dict) -> object:
        """
        Call the manager function to create an article.
        :param validated_data:
        :return:
        """
        request = self.context.get('request', None)
        headline = validated_data.get('headline', None)
        content = validated_data.get('content', None)
        author_id = request.data.get('author_id', None)
        author = get_object_or_404(User.objects.all(), id=author_id)
        published = validated_data.get('published', True)
        category = Category.objects.filter(title=headline)
        try:
            if category:
                return NewsArticle.objects.create_news_article(headline=headline,
                                                               content=content,
                                                               categories=category,
                                                               published=published,
                                                               author=author)
            category = Category.objects.create(title=headline, description=content)
            return NewsArticle.objects.create_news_article(headline=headline,
                                                           content=content,
                                                           category=category,
                                                           published=published,

                                                           author=author)
        except Exception:
            error_msg = "Headline length is limited to 255 character"
            raise serializers.ValidationError(error_msg)


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'gender', 'birth_date', 'contact_address')
