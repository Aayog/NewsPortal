from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .serializers import LoginSerializer, UserProfileSerializer, RegisterSerializer
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from .models import CustomUser, SessionToken


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # don't send token before verifying
            if user:
                return Response(
                    {
                        "message": "User registered, check email for activation",
                    },
                    status=status.HTTP_201_CREATED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        session_token = SessionToken.objects.create(user=user)
        return Response(
            {
                "token": session_token.token,
            }
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class LoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            # token, created = Token.objects.get_or_create(user=user)
            session_token = SessionToken.objects.create(user=user)
            # return Response({'token': token.key})
            url = reverse("newspost-list")
            response_data = {"token": session_token.token}
            return redirect(url, response_data)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


User = get_user_model()


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
