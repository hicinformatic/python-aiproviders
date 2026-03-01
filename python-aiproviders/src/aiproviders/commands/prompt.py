"""AI command for running agent tasks."""

from __future__ import annotations

import json

from clicommands.commands.args import parse_args_from_config
from clicommands.commands.base import Command
from clicommands.utils import format_tabulate, print_header, print_separator
from providerkit.commands.provider import _PROVIDER_COMMAND_CONFIG

from aiproviders.helpers import prompt


def _print_usage_recap(provider) -> None:
    """Print usage recap table (AI calls, input/output tokens, cost)."""
    usage = getattr(provider, "_usage", None) or {}
    steps = usage.get("steps", [])
    if not steps:
        return
    rows = []
    for i, s in enumerate(steps, 1):
        rows.append({
            "Appel": i,
            "Action": s.get("intent", ""),
            "Tokens entrant": s.get("input_tokens", 0),
            "Tokens sortant": s.get("output_tokens", 0),
            "Cost": f"{s.get('cost', 0):.4f}",
        })
    rows.append({
        "Appel": "Total",
        "Action": "",
        "Tokens entrant": usage.get("input_tokens", 0),
        "Tokens sortant": usage.get("output_tokens", 0),
        "Cost": f"{usage.get('total_cost', 0):.4f}",
    })
    print_separator()
    print_header("AI calls summary")
    print_separator()
    print(format_tabulate(rows, empty_message="Aucun appel."))


_ARG_CONFIG = {
    **_PROVIDER_COMMAND_CONFIG,
    "instruction": {"type": str, "default": ""},
    "query": {"type": str, "default": ""},
    "context": {"type": str, "default": "{}"},
    "conversation": {"type": str, "default": "[]"},
}


def _prompt_command(args: list[str]) -> bool:
    parsed = parse_args_from_config(args, _ARG_CONFIG, prog="prompt")
    kwargs = {}
    attr = parsed.get("attr")
    kwargs["attribute_search"] = attr.get("kwargs", {}) if isinstance(attr, dict) else {}
    output_format = parsed.get("format", "terminal")
    raw = parsed.pop("raw", False)
    instruction = parsed.pop("instruction") or parsed.pop("query")
    first = parsed.pop("first", False)
    context = json.loads(parsed.pop("context", "{}") or "{}")
    conversation = json.loads(parsed.pop("conversation", "[]") or "[]")
    pvs_results = prompt(
        instruction, first=first, conversation=conversation, context=context, **kwargs
    )
    for pv in pvs_results:
        name = pv["provider"].name
        time = pv["response_time"]
        print_separator()
        print_header(f"{name} - {time}s")
        print_separator()
        print(pv["provider"].response("prompt", raw=raw, output_format=output_format))
        _print_usage_recap(pv["provider"])
    return True


prompt_command = Command(_prompt_command, "Run prompt (use --instruction or --query)")
