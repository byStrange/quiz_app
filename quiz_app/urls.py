from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path("main/", include("main.urls", namespace="main")),
    path("settings/", include("settings.urls", namespace="settings")),
    path("admin/", admin.site.urls),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
