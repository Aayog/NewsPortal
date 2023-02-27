from rest_framework import serializers
from django.contrib.auth.models import update_last_login, Group, Permission
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token
from .models import CustomUser, Reporter, SessionToken
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'role')

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

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'zipcode']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        try:
            user = CustomUser.objects.get(email=email)
        except:
            raise serializers.ValidationError('The user with the email is not registered.')

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



class UserProfileSerializer(serializers.ModelSerializer):
    reporter = ReporterSerializer(required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'reporter']
        read_only_fields = ['id', 'role', 'reporter']
        permission_classes = [IsAuthenticatedOrReadOnly]
        # exclude = ('password', 'is_active')
    def create(self, validated_data):
        if validated_data.get('role') == CustomUser.REPORTER:
            reporter_data = validated_data.pop('reporter')
            user = CustomUser.objects.create_user(**validated_data)
            Reporter.objects.create(user=user, **reporter_data)

            refresh = Token.for_user(user)
            user.refresh_token = str(refresh)
            user.is_verified = False
            user.save()
            return user
        else:
            return CustomUser.objects.create_user(**validated_data)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    bio = serializers.CharField(max_length=10000, required=False)
    previous_works = serializers.CharField(max_length=10000, required=False)
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'role', 'zipcode', 'previous_works', 'bio')
        # exclude = ('password', 'is_verified', 'is_active', 'is_superuser')

    def create(self, validated_data):
        password = validated_data.pop('password')
        previous_works = validated_data.pop('previous_works')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        # Create profile
        profile_data = {'user': user.id, 'is_entry_completed': True, 'previous_works': previous_works}
        profile_serializer = UserProfileSerializer(data=profile_data)
        if profile_serializer.is_valid():
          profile_serializer.save()
        user.save()

        return user

# use can only update their own details. (validate if instance_user and update user same)
# Profile displaying/reporter and their permission listed  out (get user permissions)
# 