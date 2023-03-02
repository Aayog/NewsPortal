from django.urls import path, include
from rest_framework import routers
from .views import NewsPostViewSet, NewsPostReportViewSet, NewsPostLikeViewSet

router = routers.DefaultRouter()
router.register(r"news", NewsPostViewSet)
router.register(
    r"news/(?P<pk>\d+)/report", NewsPostReportViewSet, basename="news-post-report"
)
router.register(
    r"news/(?P<pk>\d+)/like", NewsPostLikeViewSet, basename="news-post-like"
)

urlpatterns = router.urls

urlpatterns = [
    path("", include(router.urls)),
]
