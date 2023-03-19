from rest_framework import viewsets, mixins, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .permissions import IsReporterOrAdminOrReadOnly
from .models import Category, Reporter, CustomUser, FavoriteReporters, NewsPost, FavoriteCategory
from .serializers import (
    CustomUserSerializer,
    ReporterSerializer,
    FavoriteReporterSerializer,
    CategorySerializer,
    NewsPostSerializer,
    NewsPostGetSerializer,
    NewsPostReportSerializer,
    NewsPostLikeSerializer,
    CustomUserReporterSerializer,
    FavoriteReportersSerializer,
    FavoriteCategorySerializer,  # Add this import
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]

class ReporterViewSet(viewsets.ModelViewSet):
    queryset = Reporter.objects.all()
    serializer_class = ReporterSerializer

class FavoriteReporterViewSet(viewsets.ModelViewSet):
    queryset = FavoriteReporters.objects.all()
    serializer_class = FavoriteReporterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(user=user)

class NewsPostViewSet(viewsets.ModelViewSet):
    queryset = NewsPost.objects.all()
    serializer_class = NewsPostSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsReporterOrAdminOrReadOnly,
    ]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return NewsPostGetSerializer
        return self.serializer_class

    @action(detail=True, methods=["post"], serializer_class=NewsPostReportSerializer)
    def report(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        news_post = self.get_object()
        news_post.reported_by.add(request.user)
        news_post.reported_threshold -= 1
        news_post.save()
        return Response({"message": "Post reported successfully"})

    @action(detail=True, methods=["post"], serializer_class=NewsPostLikeSerializer)
    def like(self, request, pk=None):
        news_post = self.get_object()
        user = request.user

        if news_post.liked_by.filter(id=user.id).exists():
            news_post.liked_by.remove(user)
            news_post.like_count -= 1
        else:
            news_post.liked_by.add(user)
            news_post.like_count += 1
        news_post.save()

        return Response({"message": "Post liked/unliked"}, status=status.HTTP_200_OK)

class FavoriteCategoryViewSet(viewsets.ModelViewSet):
    queryset = FavoriteCategory.objects.all()
    serializer_class = FavoriteCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)