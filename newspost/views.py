from .models import NewsPost
from .serializers import NewsPostSerializer
from .permissions import IsReporterOrAdminOrReadOnly, UserCanLikePost
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class NewsPostViewSet(viewsets.ModelViewSet):
    serializer_class = NewsPostSerializer
    queryset = NewsPost.objects.all()    
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly, IsReporterOrAdminOrReadOnly, UserCanLikePost]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
