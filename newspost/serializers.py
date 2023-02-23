from rest_framework import serializers
from .models import Reporter, CustomUser, FavoriteReporter, NewsPost

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
        model = FavoriteReporter
        fields = ['id', 'user', 'reporter']


class NewsPostSerializer(serializers.ModelSerializer):
    reporter = serializers.StringRelatedField()

    class Meta:
        model = NewsPost
        fields = '__all__'

    def create(self, validated_data):
        # check if the reporter is verified before creating the post
        reporter = validated_data.get('reporter')
        if reporter and not reporter.verified:
            raise serializers.ValidationError('Reporter is not verified')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # check if the reporter is verified before updating the post
        reporter = validated_data.get('reporter')
        if reporter and not reporter.verified:
            raise serializers.ValidationError('Reporter is not verified')
        return super().update(instance, validated_data)
