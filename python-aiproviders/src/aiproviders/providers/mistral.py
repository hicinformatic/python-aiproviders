from . import AIProviderBase

class MistralProvider(AIProviderBase):
    name = "mistral"
    display_name = "Mistral"
    description = "Mistral is a provider of AI services."
    required_packages = ["mistral"]
    config_keys = ["API_KEY"]
    config_prefix = "MISTRAL"
    models = ["mistral-large-2411"]
    abstract = True