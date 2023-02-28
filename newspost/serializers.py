from rest_framework import serializers
from .models import Category, Reporter, CustomUser, FavoriteReporters, NewsPost


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email"]


class ReporterSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Reporter
        fields = ["id", "user", "previous_works", "biography", "verified"]


# separate API, posts from favorite reporters sorted by recent
# separate API, posts from category sorted by recent
# Get reporters/ list -to favorite/unfavorite


class FavoriteReporterSerializer(serializers.ModelSerializer):
    reporter = ReporterSerializer()

    class Meta:
        model = FavoriteReporters
        fields = ["id", "user", "reporter"]


# category only changed by superuser
# liking posts if logged (Exist)
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


# Seprate for get request


class NewsPostSerializer(serializers.ModelSerializer):
    # reporter = serializers.StringRelatedField()
    categories = serializers.SlugRelatedField(
        queryset=Category.objects.all(), many=True, slug_field="name"
    )
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = NewsPost
        # fields = '__all__'
        exclude = ["created_at", "updated_at"]

    def validate(self, data):
        data.pop("author")
        data["author"] = self.context["request"].user
        if data["author"] and not data["author"].is_verified:
            raise serializers.ValidationError("Reporter is not verified")
        # if data['report_count'] >= data['reported_threshold']:
        #     data['is_hidden'] = True
        return data


class NewsPostGetSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(
        queryset=Category.objects.all(), many=True, slug_field="name"
    )

    class Meta:
        model = NewsPost
        fields = [
            "headline",
            "short_desc",
            "image",
            "like_count",
            "categories",
            "author",
            "news_text",
        ]
        read_only_fields = ("created_at", "updated_at")

    # # validate --> validate login and add author
    # def create(self, validated_data):
    #     category_data = validated_data.pop('categories')
    #     validated_data.pop('author')
    #     validated_data['author'] = self.context['request'].user
    #     if validated_data['author'] and not validated_data['author'].is_verified:
    #         raise serializers.ValidationError('Reporter is not verified')
    #     news_post = NewsPost.objects.create(**validated_data)
    #     # news_post.author.set(validated_data['author'])
    #     categories = [Category.objects.get_or_create(**cat_data)[0] for cat_data in category_data]
    #     news_post.categories.set(categories)
    #     return news_post

    # def update(self, instance, validated_data):
    #     # check if the reporter is verified before updating the post
    #     reporter = validated_data.get('reporter')
    #     if reporter and not reporter.verified:
    #         raise serializers.ValidationError('Reporter is not verified')
    #     category_names = validated_data.pop('categories', None)
    #     if category_names is not None:
    #         categories = Category.objects.filter(name__in=category_names)
    #         instance.categories.set(categories)
    #     return super().update(instance, validated_data)
