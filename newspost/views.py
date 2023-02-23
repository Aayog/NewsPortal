from rest_framework import generics
from .models import NewsPost
from .serializers import NewsPostSerializer
from .permissions import IsReporterOrAdminOrReadOnly

class NewsPostList(generics.ListCreateAPIView):
    queryset = NewsPost.objects.all()
    serializer_class = NewsPostSerializer
    permission_classes = [IsReporterOrAdminOrReadOnly]
