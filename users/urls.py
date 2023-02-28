from django.urls import path
from .views import RegisterView, LoginView, UserProfileView, ActivateAccountView
from .account import activate_account


app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("activate/<str:uidb64>/<str:token>/", activate_account, name="activate"),
]
