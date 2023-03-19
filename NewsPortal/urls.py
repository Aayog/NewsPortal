from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("users.urls")),
    path("api/", include("newspost.urls")),
    path("jet/", include("jet.urls", "jet")),
    path("auth/", include("rest_framework.urls")),
    path("", RedirectView.as_view(url="api/")),
    path("docs/", include_docs_urls(title="My API")),
]
