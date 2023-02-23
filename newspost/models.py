from django.db import models
from autoslug import AutoSlugField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from ..users.models import CustomUser, Reporter
from django.contrib.auth.models import Permission


class Category(models.Model):
    name = models.CharField(max_length=255)  
    slug = AutoSlugField(populate_from='name')
    # Categories have sub-categories
    parent_category = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='child_categories')
    description = models.TextField(blank=True, null = True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural ="Categories"

class NewsPost(models.Model):
    headline = models.CharField(max_length=150)    
    slug = AutoSlugField(populate_from='headline')
    date_added = models.DateTimeField(auto_now=True)
    short_desc = models.CharField(max_length=1000)
    news_text = models.CharField(max_length=10000)
    category = models.OneToOneField(Category, on_delete=models.CASCADE)
    author = models.OneToOneField(Reporter, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(blank=True, null=True)

    class Meta:
        permissions = (
            ("can_write_news_post", "Can write news post"),
            ("can_read_news_post", "Can read news post"),
        )
class FavoriteCategory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorite_categories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'category')
