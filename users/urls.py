from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken
from .views import UserRegistrationView, UserProfileView, CustomAuthToken, ObtainCustomAuthTokenView, LoginView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('login/', LoginView.as_view(), name='login'),    
    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
]