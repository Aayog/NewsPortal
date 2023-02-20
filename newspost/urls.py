from django.urls import path
from .views import NewsPostListView, news_detail

app_name = 'news'

urlpatterns = [
    path('', NewsPostListView.as_view(), name='news_list'),
    path('<int:pk>/', news_detail, name='news_detail'),
]