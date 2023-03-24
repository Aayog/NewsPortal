from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ActivateAccountView

app_name = "users"

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("activate/<str:token>/", ActivateAccountView.as_view(), name="activate"),
]

urlpatterns += router.urls
