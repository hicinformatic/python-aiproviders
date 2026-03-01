from . import AIProviderBase

class GoogleProvider(AIProviderBase):
    name = "google"
    display_name = "Google"
    description = "Google is a provider of AI services."
    required_packages = ["google"]
    config_keys = ["API_KEY"]
    config_prefix = "GOOGLE"
    models = ["gemini-2.5-flash"]
    abstract = True