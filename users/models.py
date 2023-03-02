from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.auth.models import Permission

# from django.core.mail import EmailMessage
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from .tokens import account_activation_token
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from .threads import send_email


class UserManager(BaseUserManager):
    def create_user(
        self, email, password=None, first_name=None, last_name=None, **extra_fields
    ):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(
            email=email, first_name=first_name, last_name=last_name, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER = 1
    REPORTER = 2
    ADMIN = 3
    ROLE_CHOICES = (
        (USER, "User"),
        (REPORTER, "Reporter"),
        (ADMIN, "ADMIN"),
    )
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    bio = models.TextField(max_length=255, null=True)
    profile_pic = models.ImageField(upload_to="profile_pictures", blank=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)  # Confirmed by email activation
    role = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES[:-1], blank=True, null=True, default=USER
    )
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    zipcode = models.CharField(max_length=30, blank=True, null=True)
    activation_token = models.CharField(max_length=50)
    is_verified = models.BooleanField(
        default=False
    )  # use this to verify if user/reporter both active and verified
    date_joined = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    objects = UserManager()

    # REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email

    def get_username(self):
        return self.email

    def email_user(self, subject, message):
        # email = EmailMessage(subject, message, to=[self.email])
        # email.content_subtype = "html"
        # email.send()
        send_email(subject, message, [self.email])

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        # Only if not set first
        if is_new:
            token = get_random_string(length=32)
            self.activation_token = token
            self.save()
            token = account_activation_token.make_token(self)
            uidb64 = urlsafe_base64_encode(force_bytes(self.pk))
            subject = "Activate Your News Portal Account"
            activation_link = f"{reverse('users:activate', kwargs={'uidb64':str(uidb64), 'token':str(token)})}"
            message = render_to_string(
                "account_activation_email.html",
                {
                    "user": self,
                    "domain": "127.0.0.1",  # current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(self.pk)),
                    # 'activation_link': f'http://127.0.0.1:9000/api/activate/{uidb64}/{token}/',
                    "activation_link": f"{settings.BASE_URL}{activation_link}",
                },
            )
            self.email_user(subject, message)
            # send mails in threads -- if running in the background -- thread/multi processing


class Reporter(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    previous_works = models.TextField(blank=True)
    biography = models.TextField(blank=True)
    verified = models.BooleanField(default=False)  # in custom user

    def __str__(self):
        return self.user.username


# use django's own
class SessionToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = account_activation_token.make_token(self.user)
        return super().save(*args, **kwargs)
