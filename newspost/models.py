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
    # date_added = models.DateTimeField(auto_now=True)
    short_desc = models.TextField()
    news_text = models.TextField()
    # only one category
    categories = models.ManyToManyField(
        Category, related_name="news_posts"
    )  # should be one to many for both ^ foreignkey
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # date wise in directory
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    reported_threshold = models.PositiveSmallIntegerField(blank=True, default=0)
    # if reported_threshold == 0 can't add report
    is_hidden = models.BooleanField(default=False)
    # report_count = models.PositiveSmallIntegerField(default=0)
    # done by serializer automatically (many to many, blank=True) search how to add from request.user if not reported_by
    reported_by = models.ManyToManyField(
        CustomUser, related_name="user_reported", blank=True
    )
    # many to many with user, similar ^
    liked_by = models.ManyToManyField(CustomUser, related_name="user_liked", blank=True)
    like_count = models.PositiveIntegerField(default=0)

    # view_count = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.slug

    # def save(self, *args, **kwargs):
    #     if self.report_count >= self.reported_threshold:
    #         self.is_hidden = True
    #     super().save(*args, **kwargs)


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
