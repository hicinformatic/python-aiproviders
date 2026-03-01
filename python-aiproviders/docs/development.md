## Development Guidelines

### General Rules

- Execute project tooling through `python dev.py <command>` or `./service.py dev <command>`.
- Default to English for all code artifacts (comments, docstrings, logging, error strings, documentation snippets, etc.).
- Keep comments minimal and only when they clarify non-obvious logic.
- Add comments only when they resolve likely ambiguity or uncertainty.

### Simplicity and Dependencies

- **Keep functions simple**: Write the simplest possible functions. Avoid unnecessary complexity.
- **Minimize dependencies**: Limit dependencies to the absolute minimum.
- **Prefer standard library**: Use Python standard library whenever possible.
- **Avoid over-engineering**: Don't add abstractions unless they solve a real problem.

### Code Quality

- **Testing**: Use pytest for all tests. Place tests in `tests/` directory.
- **Type Hints**: All public functions and methods must have complete type hints.
- **Docstrings**: Use Google-style docstrings for all public classes, methods, and functions.
- **Linting**: Follow PEP 8 and use the configured linters (ruff, mypy, etc.).

### Module Organization

- Keep related functionality grouped together in logical modules
- Maintain clear separation of concerns between modules
- Use `__init__.py` to define clean public APIs
- Avoid circular dependencies

### ProviderKit Integration

- **providerkit is an installed package**: Always use standard Python imports from `providerkit`
- **No path manipulation**: Never manipulate `sys.path` or use file paths to import providerkit modules
- **Direct imports only**: Use `from providerkit import ProviderBase` or `from providerkit.helpers import ...`

### Provider Development

- **Provider inheritance**: All providers must inherit from `AIProviderBase` (which extends `ProviderBase` from ProviderKit)
- **Required attributes**: Providers must define `name`, `display_name`, and optionally `description`
- **Service implementation**: Providers implement `_run_llm_provider_impl` and optionally `planner`, `classify`, `generate`
- **Configuration**: Use `config_keys` and `config_defaults` for provider configuration
- **API keys**: Never hardcode API keys, use environment variables with the provider's `config_prefix`

### Formats and Schemas

- **actions/*.json**: Action templates with placeholders (`{{instruction}}`, `{{context}}`, `{{conversation}}`, etc.)
- **formats/*.json**: Output type configs (description, instruction for system prompt)
- **schemas/*.json**: JSON schemas for structured output (planner, classify, generate)
- Use `get_action()`, `get_action_template()`, `get_output_type()`, `get_schema()` from `AIProviderBase`

### Error Handling

- Always handle errors gracefully
- Provide clear, actionable error messages
- Use appropriate exception types
- Handle API rate limits and failures with proper retry logic when appropriate
- Support provider fallback mechanisms for resilience

### Configuration and Secrets

- Never hardcode API keys, credentials, or sensitive information
- Use environment variables or configuration files for settings
- Use provider-specific configuration prefixes (e.g. `OPENAI_`, `SCALEWAY_`, etc.)

### Versioning

- Follow semantic versioning (SemVer)
- Document breaking changes clearly
