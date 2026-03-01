"""Admin for django_aiproviders."""

from .handle import HandleAdmin
from .provider import ProviderAdmin

__all__ = ["HandleAdmin", "ProviderAdmin"]
