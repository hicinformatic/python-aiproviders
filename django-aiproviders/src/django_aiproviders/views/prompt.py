"""Views for prompt (AI provider search)."""

from __future__ import annotations

import json
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from aiproviders.helpers import prompt as prompt_ai

from ..models import AIProviderModel


def _extract_content_and_usage(response: Any) -> tuple[str, dict[str, Any] | None]:
    """Extract content and usage from provider response (dict or JSON string)."""
    data = response
    if isinstance(response, str):
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            return response, None
    if not isinstance(data, dict):
        return str(response), None
    content = None
    usage = None
    if "Result" in data and isinstance(data["Result"], dict):
        r = data["Result"]
        content = r.get("content")
        usage = r.get("usage")
    if content is None and "raw" in data:
        raw = data["raw"]
        if isinstance(raw, dict) and "result" in raw:
            content = raw["result"].get("content") if isinstance(raw["result"], dict) else None
        if usage is None and isinstance(raw, dict) and "usage" in raw:
            usage = raw["usage"]
    if content is None:
        content = str(data)
    return content or "", usage


def _get_prompt_params(request: HttpRequest) -> tuple[str, list, str | None, bool, dict]:
    """Extract q, conversation, backend, first, context from GET or POST (JSON)."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}
        query = (data.get("q") or "").strip()
        conv = data.get("conversation")
        conversation = conv if isinstance(conv, list) else []
        backend = (data.get("bck") or "").strip() or None
        first = data.get("first") in (True, "1", 1)
        ctx = data.get("context")
        context = ctx if isinstance(ctx, dict) else {}
        return query, conversation, backend, first, context
    query = request.GET.get("q", "").strip()
    backend = request.GET.get("bck", "").strip() or None
    first = request.GET.get("first") == "1"
    conv_param = request.GET.get("conversation", "")
    conversation = []
    if conv_param:
        try:
            conversation = json.loads(conv_param)
        except json.JSONDecodeError:
            pass
    context = {}
    return query, conversation, backend, first, context


def prompt(request: HttpRequest) -> HttpResponse:
    """Run prompt via AI providers.

    GET: Page HTML or ?q=...&format=json (legacy)
    POST: JSON body {q, conversation?, bck?, first?} -> JSON response
    """
    format_type = request.GET.get("format", "html") if request.method == "GET" else "json"
    query, conversation, backend, first, context = _get_prompt_params(request)
    if request.method == "POST":
        format_type = "json"

    results = []

    if query:
        kwargs = {"first": first}
        if backend:
            kwargs["attribute_search"] = {"name": backend}
        if conversation:
            kwargs["conversation"] = conversation
        if context:
            kwargs["context"] = context
        pvs = prompt_ai(query, **kwargs)
        for pv in pvs:
            response_raw = None
            if "error" not in pv:
                try:
                    response_raw = pv["provider"].response("prompt", output_format="json")
                except Exception:
                    response_raw = None
            content, usage = _extract_content_and_usage(response_raw) if response_raw else ("", None)
            results.append({
                "provider_name": pv.get("name", ""),
                "content": content,
                "usage": usage,
                "response_time": pv.get("response_time", 0),
                "error": pv.get("error"),
            })

    if format_type == "json":
        return JsonResponse(
            {
                "results": [
                    {
                        "provider": r["provider_name"],
                        "content": r["content"],
                        "usage": r["usage"],
                        "response_time": r["response_time"],
                        "error": r["error"],
                    }
                    for r in results
                ],
                "count": len(results),
            },
            json_dumps_params={"ensure_ascii": False},
        )

    providers = AIProviderModel.objects.all()
    context = {
        "results": results,
        "query": query,
        "backend": backend,
        "first": first,
        "count": len(results),
        "providers": providers,
    }
    return render(request, "aiproviders/prompt_list.html", context)
