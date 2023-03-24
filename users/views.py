from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import LoginSerializer, UserProfileSerializer, RegisterSerializer
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from .models import CustomUser
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class UserViewSet(viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if self.action == "register":
            return RegisterSerializer
        elif self.action == "profile":
            return UserProfileSerializer
        elif self.action == "login":
            return LoginSerializer
        else:
            return super().get_serializer_class()

    @action(detail=False, methods=["POST"], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(
                    {
                        "message": "User registered, check email for activation",
                    },
                    status=status.HTTP_201_CREATED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["GET", "PUT"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def profile(self, request):
        if request.method == "GET":
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = UserProfileSerializer(
                request.user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["POST"], permission_classes=[permissions.AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.save()
            url = reverse("newspost-list")
            response_data = {"token": token}
            return Response(response_data)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class ActivateAccountView(View):
    def get(self, request, token):
        try:
            user = CustomUser.objects.get(activation_token=token)
            if not user.is_active:
                user.is_active = True
                user.activation_token = ""
                user.save()
                messages.success(request, "Your account has been activated.")
                return redirect("users:login")
            else:
                messages.warning(request, "Your account is already activated.")
                return redirect("users:login")
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid activation link.")
            return redirect("users:register")
