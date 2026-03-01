"""Handle model for tracing AI handle calls."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from django_providerkit.fields import ProviderField


class Handle(models.Model):
    """Trace of a handle call: question, provider, model, tokens consumed."""

    instruction = models.TextField(
        verbose_name=_("Instruction"),
        help_text=_("Instruction or prompt sent to the AI provider"),
    )
    conversation = models.TextField(
        verbose_name=_("Conversation"),
        help_text=_("Conversation with the AI provider"),
    )
    context = models.JSONField(
        verbose_name=_("Context"),
        help_text=_("Context sent to the AI provider"),
    )
    provider = ProviderField(
        package_name="aiproviders",
    )
    model_name = models.CharField(
        max_length=255,
        verbose_name=_("Model"),
        help_text=_("Model used (e.g., gpt-4.1, mistral-small-3.2)"),
    )
    input_tokens = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Input tokens"),
        help_text=_("Number of input tokens consumed"),
    )
    output_tokens = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Output tokens"),
        help_text=_("Number of output tokens consumed"),
    )
    response = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Response"),
        help_text=_("Response from the provider"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )

    class Meta:
        verbose_name = _("Handle")
        verbose_name_plural = _("Handles")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.provider}/{self.model_name} - {self.question[:50]}..."

    @property
    def total_tokens(self) -> int:
        """Total tokens consumed."""
        return self.input_tokens + self.output_tokens
