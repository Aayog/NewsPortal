from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


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
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    zipcode = models.CharField(max_length=30, blank=True, null=True)
    objects = UserManager()

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