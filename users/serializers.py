from rest_framework import serializers
from django.contrib.auth.models import update_last_login
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token
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


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                update_last_login(None, user)
                token, created = Token.objects.get_or_create(user=user)
                return {'user': user, 'token': token.key}
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "email" and "password".')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'is_reporter')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        refresh = Token.for_user(user)
        user.refresh_token = str(refresh)
        user.save()

        return user


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

            refresh = Token.for_user(user)
            user.refresh_token = str(refresh)
            user.save()

            return user
        else:
            return CustomUser.objects.create_user(**validated_data)
