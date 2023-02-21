from django.db import models
from autoslug import AutoSlugField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
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

    class Meta:
        verbose_name_plural ="Categories"

class NewsPost(models.Model):
    headline = models.CharField(max_length=150)
    date_added = models.DateTimeField(auto_now=True)
    short_desc = models.CharField(max_length=1000)
    news_text = models.CharField(max_length=10000)
    

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(max_length=255)
    profile_pic = models.ImageField(upload_to='profile_pictures', blank=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.username


    
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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorite_categories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'category')