from django.db import models
from autoslug import AutoSlugField
from users.models import CustomUser, Reporter
import os
from django.utils import timezone


def get_image_path(instance, filename):
    return os.path.join(
        "images",
        str(timezone.now().timestamp()) + os.path.splitext(filename)[1],
    )


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name")
    # Categories have sub-categories
    parent_category = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="child_categories",
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.slug

    class Meta:
        verbose_name_plural = "Categories"


class NewsPost(models.Model):
    headline = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from="headline")
    short_desc = models.TextField()
    news_text = models.TextField()
    categories = models.ManyToManyField(Category, related_name="news_posts")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    reported_threshold = models.PositiveSmallIntegerField(blank=True, default=0)
    is_hidden = models.BooleanField(default=False)
    reported_by = models.ManyToManyField(
        CustomUser, related_name="user_reported", blank=True
    )
    liked_by = models.ManyToManyField(CustomUser, related_name="user_liked", blank=True)
    like_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.slug


class FavoriteCategory(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="favorite_categories"
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "category")


class FavoriteReporters(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="favorite_reporters"
    )
    reporters = models.ManyToManyField(Reporter)

    class Meta:
        verbose_name_plural = "Custom user favorite reporters"
