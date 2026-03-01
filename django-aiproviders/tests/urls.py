"""URL configuration for tests."""

import django
import aiproviders
import django_aiproviders
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.conf import settings


urlpatterns = [
    path("", RedirectView.as_view(url="/admin/", permanent=False)),
    path("admin/", admin.site.urls),
    path("aiproviders/", include("django_aiproviders.urls")),
    path("geoaddress/", include("django_geoaddress.urls")),
    path("missive/", include("django_pymissive.urls")),
]

_version = f"(Django {django.get_version()}, aiproviders {aiproviders.__version__}/{django_aiproviders.__version__})"
admin.site.site_header = f"Django AIProviders - Administration {_version}"
admin.site.site_title = f"Django AIProviders Admin {_version}"
admin.site.index_title = f"Welcome to Django AIProviders {_version}"

if hasattr(settings, "NGROK_PUBLIC_URL") and settings.NGROK_PUBLIC_URL:
    admin.site.site_header += f" - {settings.NGROK_PUBLIC_URL}"
