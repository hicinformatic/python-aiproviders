from typing import Any

from . import AIProviderBase


class OpenAIProvider(AIProviderBase):
    name = "openai"
    display_name = "OpenAI"
    description = "OpenAI is a provider of AI services."
    required_packages = ["openai"]
    config_keys = ["API_KEY"]
    config_prefix = "OPENAI"
    models = ["gpt-4.1", "gpt-4.1-mini"]
    default_model = "gpt-4.1"
    abstract = True

    def request(self, payload: dict[str, Any]) -> dict[str, Any]:
        intent_type = payload.pop("type")
        service = f"openai_{intent_type}"
        if hasattr(self, service):
            return getattr(self, service)(**payload)

        
    def openai_classify(self, instruction: str, labels: list[str]) -> dict[str, Any]:
        from openai import OpenAI

        prompt = f"Classify the following instruction: {instruction} into one of the following labels: {labels}"
        client = OpenAI(api_key=self._get_config_or_env("API_KEY"))
        response = client.chat.completions.create(
            model=self.default_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        label = response.choices[0].message.content.strip()
        if label not in labels:
            raise ValueError(f"Invalid label: {label}")
        return {"classify": label}

