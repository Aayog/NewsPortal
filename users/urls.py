from django.urls import path
from .views import RegisterView, LoginView, UserProfileView, ActivateAccountView

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('activate/<str:token>/', ActivateAccountView.as_view(), name='activate_account'),
]