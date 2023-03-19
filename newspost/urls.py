from django.urls import path, include
from rest_framework import routers
from .views import (
    NewsPostViewSet,
    CategoryViewSet,
    ReporterViewSet,
    FavoriteReporterViewSet,
    FavoriteCategoryViewSet,
)

router = routers.DefaultRouter()
router.register(r"news", NewsPostViewSet)
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"reporters", ReporterViewSet, basename="reporters")
router.register(
    r"favorite-reporters", FavoriteReporterViewSet, basename="favorite-reporters"
)
router.register(
    r"favorite-categories", FavoriteCategoryViewSet, basename="favorite-categories"
)
urlpatterns = router.urls

urlpatterns = [
    path("", include(router.urls)),
]
