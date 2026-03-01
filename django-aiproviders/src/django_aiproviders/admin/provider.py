"""Admin for provider model."""

from django.contrib import admin

from django_boosted import admin_boost_view
from django_providerkit.admin.provider import BaseProviderAdmin
from virtualqueryset.queryset import VirtualQuerySet

from django_aiproviders.models import AIProviderModel
from django_aiproviders.forms.handle import TestForm

_MODELS_LIST_DISPLAY = ["id", "obj_type", "owner", "created_at", "default"]
_MODELS_EMPTY = [dict.fromkeys(_MODELS_LIST_DISPLAY, "")]
_NORMALIZED_KEY_TO_DISPLAY = {
    "id": "id",
    "object": "obj_type",
    "owner": "owner",
    "created_at": "created_at",
    "default": "default",
    "ID": "id",
    "Object": "obj_type",
    "Owner": "owner",
    "Created At": "created_at",
    "Default": "default",
}


def _normalize_model_item(item):
    """Map providerkit normalized keys to display keys (handles label vs field names)."""
    if isinstance(item, dict):
        base = dict.fromkeys(_MODELS_LIST_DISPLAY, "")
        for k, v in item.items():
            target = _NORMALIZED_KEY_TO_DISPLAY.get(k)
            if target:
                base[target] = "" if v is None else str(v)
        return base
    return dict.fromkeys(_MODELS_LIST_DISPLAY, "")


@admin.register(AIProviderModel)
class ProviderAdmin(BaseProviderAdmin):
    """Admin for AI providers."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin_boost_view("list", "Models", requires_object=True)
    def models_view(self, request, obj):
        """Display LLM models from provider.get_models()."""
        provider = getattr(obj, "_provider", None)
        if not provider or not hasattr(provider, "get_models"):
            return {"queryset": VirtualQuerySet(data=_MODELS_EMPTY), "list_display": _MODELS_LIST_DISPLAY}
        try:
            provider.call_service("get_models")
            models = provider.get_service_normalize("get_models")
        except Exception:
            return {"queryset": VirtualQuerySet(data=_MODELS_EMPTY), "list_display": _MODELS_LIST_DISPLAY}
        if isinstance(models, dict) and "error" in models:
            return {"queryset": VirtualQuerySet(data=_MODELS_EMPTY), "list_display": _MODELS_LIST_DISPLAY}
        raw = models if isinstance(models, list) else [models]
        data = [_normalize_model_item(m) for m in raw]
        default_model = getattr(provider, "default_model", None)
        if callable(default_model):
            default_model = default_model()
        if default_model:
            model_id = lambda d: d.get("id", d.get("name", "")) or ""
            for item in data:
                if model_id(item) == str(default_model):
                    item["default"] = "*"
                    break
        return {"queryset": VirtualQuerySet(data=data), "list_display": _MODELS_LIST_DISPLAY}

    @admin_boost_view("adminform", "test", requires_object=True)
    def model_view(self, request, obj):
        """Display model details."""
        return {"form": TestForm()}
        