"""Provider model for AI providers."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from virtualqueryset.models import VirtualModel
from django_providerkit.models.define import define_provider_fields, define_service_fields
from django_providerkit.managers import BaseProviderManager


services = ["prompt", "classify", "generate"]


@define_provider_fields(primary_key="name")
@define_service_fields(services)
class AIProviderModel(VirtualModel):
    """Virtual model for AI providers."""

    name: models.CharField = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
        help_text=_("Provider name (e.g., openai, scaleway)"),
        primary_key=True,
    )

    objects = BaseProviderManager(package_name="aiproviders")

    class Meta:
        managed = False
        app_label = "django_aiproviders"
        verbose_name = _("Provider")
        verbose_name_plural = _("Providers")
        ordering = ["-priority", "name"]

    def __str__(self) -> str:
        return self.display_name or self.name
