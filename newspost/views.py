from django.shortcuts import get_object_or_404

from rest_framework import mixins, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import FavoriteCategory, FavoriteReporters, NewsPost
from .permissions import IsReporterOrAdminOrReadOnly, UserCanLikePost
from .serializers import (
    CustomUserReporterSerializer,
    FavoriteReporterSerializer,
    NewsPostGetSerializer,
    NewsPostLikeSerializer,
    NewsPostReportSerializer,
    NewsPostSerializer,
)

from django.contrib.auth import get_user_model

CustomUser = get_user_model()

from rest_framework import generics


class NewsPostViewSet(viewsets.ModelViewSet):
    serializer_class = NewsPostSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsReporterOrAdminOrReadOnly,
    ]
    queryset = NewsPost.objects.all()

    def get_queryset(self):
        if self.request is not None and (
            self.request.user.is_anonymous or not self.request.user.is_authenticated
        ):
            queryset = NewsPost.objects.filter(is_hidden=False)
        elif self.request.user.is_superuser:
            queryset = NewsPost.objects.all()
        elif self.request.user.role == CustomUser.REPORTER:
            queryset = NewsPost.objects.filter(is_hidden=False)
            if self.request.method != "GET":
                queryset = queryset.filter(author=self.request.user)
        else:
            queryset = NewsPost.objects.filter(is_hidden=False)
        return queryset

    def get_serializer_class(self):
        if (
            self.request is not None
            and (
                self.request.user.is_anonymous
                or self.request.user.role == CustomUser.USER
            )
        ) and self.request.method == "GET":
            return NewsPostGetSerializer
        return NewsPostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class NewsPostReportViewSet(viewsets.GenericViewSet):
    serializer_class = NewsPostReportSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        news_post_id = kwargs["pk"]

        news_post = NewsPost.objects.get(id=news_post_id)
        news_post.reported_by.add(user)
        news_post.reported_threshold -= 1
        news_post.save()

        return Response({"message": "Post reported successfully"})


class NewsPostLikeViewSet(viewsets.GenericViewSet):
    serializer_class = NewsPostLikeSerializer
    permission_classes = [
        IsAuthenticated,
    ]


class CustomUserReporterViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CustomUserReporterSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = CustomUser.objects.filter(role=CustomUser.REPORTER)
        return queryset

    @action(detail=True, methods=["post"])
    def add_to_favorites(self, request, pk=None):
        user = request.user
        reporter = get_object_or_404(
            CustomUser.objects.filter(role=CustomUser.REPORTER), pk=pk
        )

        # Check if the reporter is already in the user's favorites
        if user.favorite_reporters.filter(reporters=reporter).exists():
            return Response({"message": "Reporter already in favorites"})

        # Add the reporter to the user's favorites
        favorite_reporters, created = FavoriteReporters.objects.get_or_create(user=user)
        favorite_reporters.reporters.add(reporter)

        return Response({"message": "Reporter added to favorites"})


class FavoriteReportersViewSet(viewsets.ModelViewSet):
    queryset = FavoriteReporters.objects.all()
    serializer_class = FavoriteReporterSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteReporterCreateAPIView(generics.CreateAPIView):
    serializer_class = FavoriteReporterSerializer

    def perform_create(self, serializer):
        reporter_ids = self.request.data.get("reporters", [])
        reporters = CustomUser.objects.filter(
            role=CustomUser.REPORTER, id__in=reporter_ids
        )
        serializer.save(user=self.request.user, reporters=reporters)
