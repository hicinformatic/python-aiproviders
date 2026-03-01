"""Admin for Handle model."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from django_aiproviders.models import Handle


@admin.register(Handle)
class HandleAdmin(admin.ModelAdmin):
    """Admin for Handle traces."""

    list_display = ["id", "provider", "model_name", "instruction_short", "input_tokens", "output_tokens", "total_tokens_display", "created_at"]
    list_filter = ["provider", "model_name", "created_at"]
    search_fields = ["instruction", "provider", "model_name"]
    readonly_fields = ["created_at"]
    fieldsets = [
        (None, {"fields": ["provider", "model_name", "instruction", ]}),
        (_("Enhanced"), {"fields": ["conversation", "context"]}),
        (_("Tokens"), {"fields": ["input_tokens", "output_tokens"]}),
        (_("Response"), {"fields": ["response"]}),
        (_("Timestamps"), {"fields": ["created_at"]}),
    ]

    def instruction_short(self, obj):
        """Truncated question for list display."""
        if len(obj.instruction) > 50:
            return obj.instruction[:50] + "..."
        return obj.instruction

    instruction_short.short_description = _("Instruction")

    def total_tokens_display(self, obj):
        """Total tokens for list display."""
        return obj.total_tokens

    total_tokens_display.short_description = _("Total tokens")
