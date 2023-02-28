from .models import NewsPost
from .serializers import NewsPostSerializer, NewsPostGetSerializer
from .permissions import IsReporterOrAdminOrReadOnly, UserCanLikePost
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Count
from users.models import CustomUser


class NewsPostViewSet(viewsets.ModelViewSet):
    serializer_class = NewsPostSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsReporterOrAdminOrReadOnly,
        UserCanLikePost,
    ]
    queryset = NewsPost.objects.all()

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            queryset = NewsPost.objects.filter(is_hidden=False)
        elif self.request.user.is_superuser:
            queryset = NewsPost.objects.all()
        elif self.request.user.role == CustomUser.REPORTER:
            queryset = NewsPost.objects.filter(
                is_hidden=False, author=self.request.user
            )
        else:
            queryset = NewsPost.objects.filter(is_hidden=False)
        return queryset

    def get_serializer_class(self):
        if self.request.user.role == CustomUser.USER and self.request.method == "GET":
            return NewsPostGetSerializer
        return NewsPostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# separate api to like isAuthenticate or can report
