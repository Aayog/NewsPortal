from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import Permission


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, first_name=None, last_name=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name,  **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser):
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    bio = models.TextField(max_length=255, null=True)
    profile_pic = models.ImageField(upload_to='profile_pictures', blank=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    is_reporter = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    zipcode = models.CharField(max_length=30, blank=True, null=True)
    objects = UserManager()
    date_joined = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'email'    
    EMAIL_FIELD = 'email'
    # REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email 
    
    def get_username(self):
        return self.email
    
    def has_perm(self, perm, obj=None): 
        return self.is_superuser

    def has_module_perms(self, app_label): 
        return self.is_superuser

class Reporter(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    previous_works = models.TextField(blank=True)
    biography = models.TextField(blank=True)
    verified = models.BooleanField(default=False) #in custom user

    def __str__(self):
        return self.user.username

class FavoriteReporters(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorite_reporters')
    reporters = models.ManyToManyField(Reporter)

    class Meta:
        verbose_name_plural = "Custom user favorite reporters"

# Custom Permissions
class ReporterPermissions(models.Model):
    class Meta:
        managed = False  # no database table creation or deletion operations will be performed for this model.
        default_permissions = ()
        permissions = (
            ("can_write_news_post", "Can write news post"),
            ("can_read_news_post", "Can read news post"),
        )

class AdminPermissions(models.Model):
    class Meta:
        managed = False  # no database table creation or deletion operations will be performed for this model.
        default_permissions = ()
        permissions = (
            ("can_write_news_post", "Can write news post"),
            ("can_read_news_post", "Can read news post"),
        )

