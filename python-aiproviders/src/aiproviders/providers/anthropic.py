from . import AIProviderBase

class AnthropicProvider(AIProviderBase):
    name = "anthropic"
    display_name = "Anthropic"
    description = "Anthropic is a provider of AI services."
    required_packages = ["anthropic"]
    config_keys = ["API_KEY"]
    config_prefix = "ANTHROPIC"
    models = ["claude-3-5-sonnet-20240620"]

    abstract = True