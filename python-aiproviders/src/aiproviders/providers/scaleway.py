import json
import urllib.request
from datetime import datetime
from typing import Any

from . import AIProviderBase

class ScalewayProvider(AIProviderBase):
    name = "scaleway"
    display_name = "Scaleway"
    description = "Scaleway is a provider of AI services."
    required_packages = ["openai"]
    config_keys = ["API_SECRET_KEY", "BASE_URL"]
    config_defaults = {
        "BASE_URL": "https://api.scaleway.ai/v1",
    }
    models = [
        "deepseek-r1-distill-llama-70b",
        "llama-3.3-70b-instruct",
        "mistral-nemo-instruct-2407",
        "llama-3.1-8b-instruct",
        "pixtral-12b-2409",
        "gemma-3-27b-it",
        "bge-multilingual-gemma2",
        "qwen3-235b-a22b-instruct-2507",
        "mistral-small-3.2-24b-instruct-2506",
        "qwen3-coder-30b-a3b-instruct",
        "gpt-oss-120b",
        "voxtral-small-24b-2507",
        "whisper-large-v3",
        "qwen3-embedding-8b",
        "holo2-30b-a3b",
        "devstral-2-123b-instruct-2512",
    ]
    fields_associations = {
        "id": "id",
        "object": "object",
        "owner": "owned_by",
        "created_at": "created",
    }

    _default_model_fallback = "mistral-small-3.2-24b-instruct-2506"

    @property
    def default_model(self) -> str:
        """Default LLM model to use (from API or fallback)."""
        model_id = lambda m: m.get("id", m.get("name", ""))
        cached = getattr(self, "_service_results_cache", {}).get("get_models", {}).get("result")
        models = cached if isinstance(cached, list) else self.get_models()
        match = next(
            (m for m in models if "mistral" in model_id(m).lower() and "small" in model_id(m).lower()),
            next((m for m in models if "mistral" in model_id(m).lower()), None),
        )
        return model_id(match) if match else self._default_model_fallback

    def get_normalize_default(self, data: dict[str, Any]) -> str:
        """Return '*' if model is the default, else ''."""
        model_id = data.get("id", data.get("name", "")) or ""
        return "*" if model_id and model_id == self.default_model else ""

    def get_normalize_created_at(self, data: dict[str, Any]) -> str:
        """Transform Unix timestamp to readable date."""
        ts = data.get("created") or data.get("created_at")
        if ts is None:
            return ""
        try:
            return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, OSError):
            return str(ts)

    def get_models(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Fetch available LLM models from Scaleway API."""
        base_url = self._get_config_or_env("BASE_URL")
        api_key = self._get_config_or_env("API_SECRET_KEY")
        url = f"{base_url.rstrip('/')}/models"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
        return data.get("data", data) if isinstance(data, dict) else data

    def _run_llm_provider_impl(self, payload: dict[str, Any]) -> dict[str, Any]:
        intent_type = payload.pop("type")
        service = f"scaleway_{intent_type}"
        if hasattr(self, service):
            return getattr(self, service)(**payload)
        return self._chat_completion_generic(intent_type, **payload)

    @property
    def client(self):
        from openai import OpenAI
        return OpenAI(
            api_key=self._get_config_or_env("API_SECRET_KEY"),
            base_url=self._get_config_or_env("BASE_URL"),
        )

    def _render_messages(self, format_data: dict[str, str], values: dict[str, Any]) -> list[dict[str, str]]:
        """Build messages from format template, replacing {{key}} with values."""
        _empty = "—"
        messages = []
        for role, template in format_data.items():
            content = template
            for key, val in values.items():
                if val is None or val in ([], {}):
                    replacement = _empty
                elif isinstance(val, str):
                    replacement = val
                else:
                    replacement = json.dumps(val, ensure_ascii=False)
                content = content.replace(f"{{{{{key}}}}}", replacement)
            messages.append({"role": role, "content": content})
        return messages

    def _wrap_schema(self, schema: dict[str, Any], name: str) -> dict[str, Any]:
        """Wrap schema for Scaleway output_type."""
        return {"type": "json_schema", "json_schema": {"name": name, "schema": schema}}

    def _chat_completion(self, name: str, schema_name: str | None = None, **kwargs: Any) -> dict[str, Any]:
        fmt_name = kwargs.pop("output_type", "json")
        format_data = self.get_action_template(name, fmt_name)
        fmt_config = self.get_output_type(fmt_name)
        kwargs["output_type"] = fmt_name

        if fmt_name == "json":
            schema = kwargs.pop("schema", None) or self.get_schema(name).copy()
            api_output_type = self._wrap_schema(schema, schema_name or f"{name.title()}Response")
        else:
            api_output_type = None

        messages = self._render_messages(format_data, kwargs)
        create_kw: dict[str, Any] = {
            "model": self.default_model,
            "messages": messages,
            "temperature": 0.0,
        }
        if api_output_type:
            create_kw["response_format"] = api_output_type  # API param name
        response = self.client.chat.completions.create(**create_kw)
        return self._parse_response(response, output_type=fmt_name, format_config=fmt_config)

    def _parse_response(self, response: Any, output_type: str = "json", format_config: dict | None = None) -> dict[str, Any]:
        result: dict[str, Any] = {}
        content = response.choices[0].message.content or ""
        if output_type == "json" and content:
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                result = {"content": content}
        else:
            result = {"content": content, "format": output_type}
        if hasattr(response, "usage") and response.usage:
            usage = response.usage
            result["usage"] = {
                "input_tokens": getattr(usage, "prompt_tokens", 0) or 0,
                "output_tokens": getattr(usage, "completion_tokens", 0) or 0,
                "total_tokens": getattr(usage, "total_tokens", 0) or 0,
                "total_cost": 0.0,
            }
        return result

    def scaleway_planner(self, **kwargs: Any) -> dict[str, Any]:
        intents = kwargs.get("intents", self.available_intents)
        formats = kwargs.get("formats", self.available_formats)
        schema_planner = self.get_schema("planner.schema").copy()
        schema_planner["properties"]["intent"]["enum"] = intents
        schema_planner["properties"]["format"]["enum"] = formats
        result = self._chat_completion("planner", schema=schema_planner, **kwargs)
        result.setdefault("confidence", 1.0)
        return result

    def scaleway_classify(self, **kwargs: Any) -> dict[str, Any]:
        labels = kwargs.get("labels", kwargs.get("intents", self.available_intents))
        schema_classify = self.get_schema("classify").copy()
        schema_classify["properties"]["classify"]["enum"] = labels
        result = self._chat_completion("classify", schema=schema_classify, **kwargs)
        label = result.get("classify", "").strip()
        if label not in labels:
            raise ValueError(f"Invalid label: {label}")
        confidence = result.get("confidence")
        if confidence is not None:
            result["confidence"] = float(confidence)
        else:
            result["confidence"] = 1.0
        return result

    def scaleway_generate(self, **kwargs: Any) -> dict[str, Any]:
        output_type = kwargs.get("output_type", "json")
        schema = self.get_combined_schema("generate", output_type)
        return self._chat_completion(
            "generate",
            schema=schema,
            schema_name="GenerateResponse",
            **kwargs,
        )

    def _chat_completion_generic(self, intent_type: str, **kwargs: Any) -> dict[str, Any]:
        """Generic handler for intents with action+schema (extract, summarize, translate, etc.)."""
        output_type = kwargs.get("output_type", "json")
        schema = self.get_combined_schema(intent_type, output_type)
        return self._chat_completion(
            intent_type,
            schema=schema,
            schema_name=f"{intent_type.title()}Response",
            **kwargs,
        )