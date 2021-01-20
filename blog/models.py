import uuid

from django.db import models

# Create your models here.
from blog.managers import NewsArticleManager, CategoryManager


class Address(models.Model):
    """
    Address model class. Only supported via admin creation
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    street = models.CharField(max_length=255, blank=True)
    zip = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Category(models.Model):
    """
    The category defined for the newspaper article to sort in future if necessary
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text='Category Id')

    title = models.CharField(max_length=24, default='', blank=False, null=False, help_text='Category Title')
    description = models.CharField(max_length=200, blank=False, null=False, help_text='Category Description')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    options = {
                  'db_table': 'Category',
                  'managed': False,
              },

    def __str__(self):
        return "id: %s title: %s" % (self.id, self.title)

    objects = CategoryManager()


class User(models.Model):
    """
    User model to create user object
    Note user creation only supported via admin and so is its address object
    """
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"
    UNKNOWN = "U"

    GENDER_CHOICES = [
        (MALE, "Male"),
        (FEMALE, "Female"),
        (OTHER, "Other"),
        (UNKNOWN, "Unknown"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(max_length=255, verbose_name='email address', unique=True, help_text='User Email')
    first_name = models.CharField(max_length=255, blank=True, editable=True, help_text=' User First Name')
    last_name = models.CharField(max_length=255, blank=True, help_text='User Last Name')
    gender = models.CharField(max_length=16, choices=GENDER_CHOICES, default=UNKNOWN,
                              help_text='Gender choice M, F, O, U')
    birth_date = models.DateField(null=True, help_text=' Date of birth of user')
    contact_address = models.OneToOneField(Address, on_delete=models.CASCADE, default=None, blank=True, null=True,
                                           help_text='User Contact address related to address class ')


class NewsArticle(models.Model):
    """
    News article model object that hold the detailed news and can also be autored by user and divided in categories
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    headline = models.CharField(max_length=200, unique=True, blank=False, null=False, help_text='News article headline')
    content = models.TextField(blank=False, null=False, help_text='News content')
    published = models.BooleanField(default=True)

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='news_article_post',
                               related_query_name='news_article_posts',
                               blank=False,
                               null=False,
                               help_text='News authored by user')

    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 related_name='article_category',
                                 related_query_name='article_categories',
                                 help_text='News category')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = NewsArticleManager()

    def __str__(self):
        return "id: %s author: %s" % (self.id, self.author.email)
