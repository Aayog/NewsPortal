from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .serializers import RegistrationSerializer, UserProfileSerializer
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .forms import RegistrationForm
from django.contrib.auth import get_user_model
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .admin import EmailBackend
from rest_framework import generics, permissions
from .models import Reporter, CustomUser
from ..newspost.models import FavoriteReporter
from ..newspost.serializers import ReporterSerializer, CustomUserSerializer, FavoriteReporterSerializer

User = get_user_model()

class UserRegistrationView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (AllowAny,)
    def post(self, request):        
        email = request.data.get('email')
        password = request.data.get('password')
        data = {'email': email, 'password': password}

        serializer = RegistrationSerializer(data=data)
        if serializer.is_valid():
            user = User.objects.create_user(email=email, password=password)
            token = Token.objects.create(user=user)
            response_data = {
                'token': token.key,
                'user': UserProfileSerializer(user).data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def register(request):
    form = RegistrationForm(request.POST)
    if form.is_valid():
        user = form.save()
        return Response({'success': 'User registered successfully!'})
    return Response({'error': form.errors}, status=status.HTTP_400_BAD_REQUEST)

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if not user.is_active:
            return Response({'error': 'User account is disabled.'}, 
                            status=status.HTTP_401_UNAUTHORIZED)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

class ObtainCustomAuthTokenView(CustomAuthToken):
    permission_classes = []
    authentication_classes = []
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserProfileSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        print(email, password)
        user = EmailBackend().authenticate(request, email=email, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Unable to log in with provided credentials.'})

class ReporterList(generics.ListCreateAPIView):
    queryset = Reporter.objects.all()
    serializer_class = ReporterSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ReporterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reporter.objects.all()
    serializer_class = ReporterSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CustomUserList(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class CustomUserDetail(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class FavoriteReporterList(generics.ListCreateAPIView):
    queryset = FavoriteReporter.objects.all()
    serializer_class = FavoriteReporterSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class FavoriteReporterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = FavoriteReporter.objects.all()
    serializer_class = FavoriteReporterSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]