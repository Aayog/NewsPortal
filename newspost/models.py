from django.db import models
from autoslug import AutoSlugField
from django.contrib.auth.models import AbstractBaseUser
from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)  
    slug = AutoSlugField(populate_from='name')
    # Categories have sub-categories
    parent_category = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='child_categories')
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name
    
class NewsPost(models.Model):
    headline = models.CharField(max_length=150)
    date_added = models.DateTimeField(auto_now=True)
    short_desc = models.CharField(max_length=1000)
    news_text = models.CharField(max_length=10000)
    

class CustomUser(AbstractBaseUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(max_length=255)
    profile_pic = models.ImageField(upload_to='/profile_pictures', blank=True)

    
class Reporter(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    previous_works = models.TextField(blank=True)
    biography = models.TextField(blank=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class FavoriteReporter(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorite_reporters')
    reporter = models.ForeignKey(Reporter, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'reporter')

class FavoriteCategory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorite_reporters')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'category')