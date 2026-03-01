## Assistant Guidelines

This file provides general guidelines for the AI assistant working on this project.

For detailed information, refer to:
- `AI.md` – Condensed reference guide for AI assistants (start here)
- `purpose.md` – Project purpose and goals
- `structure.md` – Project structure and module organization
- `agent.md` – Agent architecture (planner, loop, formats, schemas)
- `development.md` – Development guidelines and best practices

### Quick Reference

- Use `./service.py dev <command>` or `python dev.py <command>` for project tooling
- Use `./service.py quality <command>` or `python quality.py <command>` for quality checks
- Maintain clean module organization and separation of concerns
- Default to English for all code artifacts
- Follow Python best practices and quality standards
- Keep dependencies minimal and prefer standard library

### aiproviders-Specific Guidelines

- **Provider development**: All providers must inherit from `AIProviderBase` and implement `_run_llm_provider_impl` (and optionally planner, classify, generate)
- **ProviderKit integration**: Use ProviderKit for provider management, discovery, and configuration
- **API keys**: Never hardcode API keys, use environment variables with provider-specific prefixes
- **Structured output**: Use JSON schemas and format templates for consistency

### Provider Implementation Checklist

When creating a new provider:
- [ ] Inherit from `AIProviderBase`
- [ ] Define `name`, `display_name`, and `description`
- [ ] Set `required_packages` and `config_keys` if needed
- [ ] Implement `_run_llm_provider_impl` and optionally `{provider}_planner`, `{provider}_classify`, `{provider}_generate`
- [ ] Use actions, formats and schemas from `actions/`, `formats/` and `schemas/`
- [ ] Handle errors gracefully
