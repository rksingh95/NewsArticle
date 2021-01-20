# Register your models here.

from django.contrib import admin

from .models import User, NewsArticle, Category, Address


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'gender', 'birth_date', 'contact_address')
    search_fields = ['id', 'email', 'first_name', 'last_name']


class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'street', 'zip', 'city',)
    search_fields = ['id', 'zip', 'city', ]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description',)
    search_fields = ['id', ]


class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'headline', 'content', 'author_email', 'created_at',
                    'updated_at')
    search_fields = ['headline', 'content', 'author__id', 'author__email']

    @staticmethod
    def author_email(obj):
        return obj.author.email


admin.site.register(User, UserAdmin)
admin.site.register(NewsArticle, NewsArticleAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Category, CategoryAdmin)