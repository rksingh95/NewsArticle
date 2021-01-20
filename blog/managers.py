from django.db import models

# Managers to create the model objects in PosgresDB

class CategoryManager(models.Manager):
    def create_category(self, title, description, **kwargs):
        """
        category manager
        :param title:
        :param description:
        :param kwargs:
        :return:
        """
        category = self.model(title=title,
                              description=description, )
        category.save()
        return category


class NewsArticleManager(models.Manager):
    def create_news_article(self, headline, content, published=True, author=None, category=None, **kwargs):
        """
        Manager to create news article
        :param headline:
        :param content:
        :param published:
        :param author:
        :param category:
        :param kwargs:
        :return:
        """
        article = self.model(headline=headline,
                             content=content,
                             published=published,
                             author=author,
                             category=category)
        article.save()
        return article
