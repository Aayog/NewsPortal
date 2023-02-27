from rest_framework import serializers
from .models import Category, Reporter, CustomUser, FavoriteReporters, NewsPost

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']

class ReporterSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    class Meta:
        model = Reporter
        fields = ['id', 'user', 'previous_works', 'biography', 'verified']

class FavoriteReporterSerializer(serializers.ModelSerializer):
    reporter = ReporterSerializer()
    class Meta:
        model = FavoriteReporters
        fields = ['id', 'user', 'reporter']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class NewsPostSerializer(serializers.ModelSerializer):
    # reporter = serializers.StringRelatedField()
    categories = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        many=True,
        slug_field='name'
    )
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = NewsPost
        # fields = '__all__'
        exclude = ['created_at', 'updated_at']

    def create(self, validated_data):
        category_data = validated_data.pop('categories')
        validated_data.pop('author')
        validated_data['author'] = self.context['request'].user
        if validated_data['author'] and not validated_data['author'].is_verified:
            raise serializers.ValidationError('Reporter is not verified')
        news_post = NewsPost.objects.create(**validated_data)        
        # news_post.author.set(validated_data['author'])
        categories = [Category.objects.get_or_create(**cat_data)[0] for cat_data in category_data]
        news_post.categories.set(categories)
        return news_post

    def update(self, instance, validated_data):
        # check if the reporter is verified before updating the post
        reporter = validated_data.get('reporter')
        if reporter and not reporter.verified:
            raise serializers.ValidationError('Reporter is not verified')
        category_names = validated_data.pop('categories', None)
        if category_names is not None:
            categories = Category.objects.filter(name__in=category_names)
            instance.categories.set(categories)
        return super().update(instance, validated_data)
