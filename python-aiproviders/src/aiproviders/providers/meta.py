from . import AIProviderBase


class MetaProvider(AIProviderBase):
    name = "meta"
    display_name = "Meta"
    description = "Meta is a provider of AI services."
    required_packages = ["meta"]
    config_keys = ["API_KEY"]
    config_prefix = "META"
    models = ["meta-llama-3-8b-instruct"]
    abstract = True