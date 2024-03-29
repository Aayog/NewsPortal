from rest_framework import serializers
from .models import (
    Category,
    Reporter,
    CustomUser,
    FavoriteReporters,
    NewsPost,
    FavoriteCategory,
)
from django.shortcuts import get_object_or_404
from django.urls import reverse


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email"]


class ReporterSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Reporter
        fields = ["id", "user", "previous_works", "biography", "verified"]


# separate API, posts from favorite reporters sorted by recent
# separate API, posts from category sorted by recent
# Get reporters/ list -to favorite/unfavorite


class FavoriteReporterSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    reporters = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role=CustomUser.REPORTER), many=True
    )

    class Meta:
        model = FavoriteReporters
        fields = ["id", "user", "reporters"]


# category only changed by superuser
# liking posts if logged (Exist)
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


# Seprate for get request


class NewsPostSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(
        queryset=Category.objects.all(), many=True, slug_field="name"
    )
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = NewsPost
        # fields = '__all__'
        exclude = ["reported_by"]
        read_only = ["author", "created_at", "updated_at", "like_count"]

    def validate(self, data):
        # data.pop("author")
        # pop

        data["author"] = self.context["request"].user
        # is_authenticated/loggedin check role
        if data["author"] and not data["author"].is_authenticated:
            raise serializers.ValidationError("Reporter is not logged in")

        if data["author"] and not data["author"].is_verified:
            raise serializers.ValidationError("Reporter is not verified")

        reported_threshold = data.get("reported_threshold", None)
        if reported_threshold is not None and reported_threshold <= 0:
            raise serializers.ValidationError("This post cannot be reported")
        reported_by = data.get("reported_by", None)
        if reported_by:
            reported_by = CustomUser.objects.filter(
                pk__in=[user.pk for user in reported_by]
            )
            user = self.context["request"].user
            if reported_by.filter(id=user.id).exists():
                raise serializers.ValidationError("You have already reported this post")
        return data


class NewsPostGetSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(
        queryset=Category.objects.all(), many=True, slug_field="name"
    )

    class Meta:
        model = NewsPost
        fields = [
            "id",
            "headline",
            "short_desc",
            "image",
            "like_count",
            "categories",
            "author",
            "news_text",
        ]
        read_only_fields = ("created_at", "updated_at")


class NewsPostReportSerializer(serializers.Serializer):
    reported_reason = serializers.CharField(max_length=255)

    def validate(self, data):
        user = self.context["request"].user
        news_post_id = self.context["view"].kwargs["pk"]

        if NewsPost.objects.filter(id=news_post_id, reported_by=user).exists():
            raise serializers.ValidationError("You have already reported this post")
        return data


class NewsPostLikeSerializer(serializers.Serializer):
    def validate(self, data):
        user = self.context["request"].user
        news_post_id = self.context["view"].kwargs["pk"]
        news_post = get_object_or_404(NewsPost, id=news_post_id)

        if news_post.liked_by.filter(id=user.id).exists():
            # User has already liked the post, so unlike
            news_post.liked_by.remove(user)
            news_post.like_count -= 1
            news_post.save()
        else:
            # User has not liked the post before, so increase the like count
            news_post.liked_by.add(user)
            news_post.like_count += 1
            news_post.save()
        return data


class CustomUserReporterSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    news_posts = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["id", "email", "full_name", "news_posts"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_news_posts(self, obj):
        news_posts = NewsPost.objects.filter(author=obj)[:5]
        serializer = NewsPostGetSerializer(news_posts, many=True, context=self.context)
        data = serializer.data
        for i in range(len(data)):
            data[i]["api_url"] = reverse("newspost-detail", args=[data[i]["id"]])
        return data


class FavoriteReportersSerializer(serializers.ModelSerializer):
    reporters = ReporterSerializer(many=True)

    class Meta:
        model = FavoriteReporters
        fields = ["id", "reporters"]


class FavoriteCategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = FavoriteCategory
        fields = ["id", "user", "category"]
