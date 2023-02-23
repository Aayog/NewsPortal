from rest_framework import serializers
from .models import CustomUser, Reporter

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'is_reporter')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ReporterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reporter
        fields = ['previous_works', 'biography', 'verified']

class UserProfileSerializer(serializers.ModelSerializer):
    reporter = ReporterSerializer(required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'is_reporter', 'reporter']
        read_only_fields = ['id', 'is_reporter', 'reporter']

    def create(self, validated_data):
        if validated_data.get('is_reporter'):
            reporter_data = validated_data.pop('reporter')
            user = CustomUser.objects.create_user(**validated_data)
            Reporter.objects.create(user=user, **reporter_data)
            return user
        else:
            return CustomUser.objects.create_user(**validated_data)