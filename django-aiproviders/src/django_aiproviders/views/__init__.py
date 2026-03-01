"""Views for django_aiproviders."""

from django.shortcuts import render

from .prompt import prompt


def widget(request):
    """Return widget HTML fragment for AJAX."""
    return render(request, "aiproviders/widget.html")


def assistant(request):
    """Test page for the widget (inputs + text area to trigger the icon)."""
    return render(request, "aiproviders/assistant.html")


__all__ = ["widget", "assistant", "prompt"]
