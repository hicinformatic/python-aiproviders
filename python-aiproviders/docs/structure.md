## Project Structure

aiproviders follows a standard Python package structure with a provider-based architecture using ProviderKit for provider management.

### General Structure

```
python-aiproviders/
├── src/
│   └── aiproviders/           # Main package directory
│       ├── __init__.py        # Package exports
│       ├── providers/         # AI provider implementations
│       │   ├── __init__.py    # AIProviderBase base class
│       │   ├── actions/       # Action templates (JSON)
│       │   │   ├── planner.json
│       │   │   ├── classify.json
│       │   │   └── generate.json
│       │   ├── formats/       # Output type configs (json, html, text, xml, csv)
│       │   └── schemas/       # JSON schemas for structured output
│       │   ├── openai.py      # OpenAI provider
│       │   ├── anthropic.py   # Anthropic provider
│       │   ├── google.py      # Google provider
│       │   ├── mistral.py     # Mistral provider
│       │   ├── meta.py        # Meta provider
│       │   └── scaleway.py    # Scaleway provider
│       ├── commands/          # CLI commands
│       │   ├── __init__.py
│       │   └── prompt.py      # Prompt command
│       ├── helpers.py         # get_ai_providers, handle, etc.
│       ├── cli.py             # CLI interface
│       └── __main__.py        # Entry point for package execution
├── docs/                      # Documentation
├── service.py                 # Service entry point script
├── pyproject.toml             # Project configuration
└── README.md
```

### Module Organization Principles

- **Single Responsibility**: Each module should have a clear, single purpose
- **Separation of Concerns**: Keep different concerns in separate modules
- **Provider-Based Architecture**: Providers inherit from ProviderKit's ProviderBase via AIProviderBase
- **Clear Exports**: Use `__init__.py` to define public API
- **Logical Grouping**: Organize related functionality together

### Provider Organization

The `providers/` directory contains AI provider implementations:

- **`__init__.py`**: Defines `AIProviderBase` base class that extends `ProviderBase` from ProviderKit
- **`actions/`**: JSON templates for prompts with placeholders (`{{instruction}}`, `{{context}}`, `{{conversation}}`, etc.)
- **`formats/`**: Output type configs (json, html, text, xml, csv)
- **`schemas/`**: JSON schemas for structured output (classify, generate)
- Each provider file implements `_run_llm_provider_impl` and optionally `{provider}_planner`, `{provider}_classify`, `{provider}_generate`

### Helper Functions

The `helpers.py` module provides:
- `get_ai_providers()`: Get AI providers from various sources
- `get_ai_provider()`: Get a specific provider by attribute search
- `prompt()`: Run agent loop (plan → execute → memory) using AI providers

### ProviderKit Integration

aiproviders uses ProviderKit for provider management:
- Providers inherit from `ProviderBase` via `AIProviderBase`
- Uses ProviderKit's helper functions for provider discovery and management
- Providers can be loaded from JSON, configuration, or directory scanning
