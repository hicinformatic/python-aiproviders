"""Command to list LLM models from providers (e.g. Scaleway)."""

from __future__ import annotations

from clicommands.commands.args import parse_args_from_config
from clicommands.commands.base import Command
from clicommands.utils import print_header, print_separator
from providerkit.commands.provider import _PROVIDER_COMMAND_CONFIG

from aiproviders.helpers import get_models


_ARG_CONFIG = {
    **_PROVIDER_COMMAND_CONFIG,
}


def _models_command(args: list[str]) -> bool:
    parsed = parse_args_from_config(args, _ARG_CONFIG, prog="models")
    kwargs = {}
    attr = parsed.get("attr")
    kwargs["attribute_search"] = attr.get("kwargs", {}) if isinstance(attr, dict) else {}
    output_format = parsed.get("format", "terminal")
    raw = parsed.pop("raw", False)
    first = parsed.pop("first", False)
    pvs_results = get_models(first=first, **kwargs)
    for pv in pvs_results:
        if "error" in pv:
            print_separator()
            print_header(f"{pv.get('name', 'provider')} - error")
            print_separator()
            print(pv["error"])
            continue
        provider = pv["provider"]
        time = pv["response_time"]
        print_separator()
        print_header(f"{provider.display_name} - {time}s")
        print_separator()
        print(provider.response("get_models", raw=raw, output_format=output_format))
    return True


models_command = Command(_models_command, "List LLM models (get_models service)")
