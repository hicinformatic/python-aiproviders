"""Manager for AI providers."""

from django_providerkit.managers import BaseProviderManager


class ProviderManager(BaseProviderManager):
    """Manager for AI providers."""

    package_name = "aiproviders"
