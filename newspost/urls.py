from django.urls import path, include
from rest_framework import routers
from .views import NewsPostViewSet

router = routers.DefaultRouter()
router.register(r'news', NewsPostViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
