"""URL configuration for django_aiproviders."""

from django.urls import path

from . import views

urlpatterns = [
    path("widget/", views.widget, name="aiproviders_widget"),
    path("assistant/", views.assistant, name="aiproviders_assistant"),
    path("prompt/", views.prompt, name="aiproviders_prompt"),
]
