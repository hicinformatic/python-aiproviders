# aiproviders

Python library for AI provider management. Provides a unified interface to multiple AI providers (OpenAI, Anthropic, Google, Mistral, Meta, Scaleway, etc.) using [ProviderKit](https://github.com/hicinformatic/python-providerkit).

## Installation

```bash
pip install aiproviders
```

## Requirements

- Python >= 3.10
- [providerkit](https://github.com/hicinformatic/python-providerkit)
- [clicommands](https://github.com/hicinformatic/python-clicommands)

## Quick Start

```python
from aiproviders.helpers import get_ai_providers, prompt

# List available providers
providers = get_ai_providers()

# Run prompt task across providers
results = prompt("Your instruction here", first=True)
```

## CLI

```bash
# List commands
aiproviders

# List providers
aiproviders provider --list

# Run prompt with an instruction
aiproviders prompt --instruction "Your instruction"
```

## Configuration

Set API keys via environment variables with provider-specific prefixes:

| Provider   | Variable                | Example              |
|------------|-------------------------|----------------------|
| OpenAI     | `OPENAI_API_KEY`        | Your OpenAI API key  |
| Anthropic  | `ANTHROPIC_API_KEY`     | Your Anthropic key   |
| Scaleway   | `SCALEWAY_API_SECRET_KEY`    | Your Scaleway key |
| Scaleway   | `SCALEWAY_BASE_URL`     | `https://api.scaleway.ai/v1` (default) |

## Supported Providers

- **OpenAI** – GPT models
- **Anthropic** – Claude models
- **Google** – Gemini models
- **Mistral** – Mistral models
- **Meta** – Llama models
- **Scaleway** – Generative APIs (Llama, Mistral, Qwen, etc.)

## Services

Providers implement services such as:

- **prompt** – Agent loop: plan (intent + format) → execute → memory
- **run_llm_provider** – Low-level LLM dispatch (planner, generate, classify, etc.)
- **classify** – Intent classification with labels
- **generate** – Document generation with instruction, conversation, context

## Project Structure

```
python-aiproviders/
├── src/aiproviders/
│   ├── providers/         # AI provider implementations
│   │   ├── actions/       # Action templates (planner, generate, classify...)
│   │   ├── formats/       # Output type configs (json, html, text, xml, csv)
│   │   └── schemas/       # JSON schemas for structured output
│   ├── commands/         # CLI commands
│   └── helpers.py         # get_ai_providers, prompt, etc.
├── docs/
├── pyproject.toml
└── README.md
```

## Adding a Provider

1. Create `src/aiproviders/providers/your_provider.py`
2. Inherit from `AIProviderBase`
3. Define `name`, `display_name`, `config_keys`
4. Implement `_run_llm_provider_impl` and optionally `scaleway_planner`, `scaleway_generate`, `scaleway_classify`, etc.

## Documentation

- [docs/purpose.md](docs/purpose.md) – Project purpose and goals
- [docs/structure.md](docs/structure.md) – Project structure
- [docs/agent.md](docs/agent.md) – Agent architecture (planner, loop, formats, schemas)
- [docs/development.md](docs/development.md) – Development guidelines
- [docs/AI.md](docs/AI.md) – AI assistant guidelines

## License

MIT
