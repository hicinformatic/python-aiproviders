## Project Purpose

**aiproviders** is a Python library for AI provider management. It provides a unified interface to multiple AI providers (OpenAI, Anthropic, Google, Mistral, Meta, Scaleway, etc.) using ProviderKit for provider management.

### Core Functionality

The library enables you to:

1. **Manage multiple AI providers** through ProviderKit:
   - Provider discovery and enumeration
   - Provider selection and fallback mechanisms
   - Configuration management per provider
   - Dependency validation (API keys, packages)

2. **Run AI tasks** across providers:
   - Prompt: agent loop (plan intent+format → execute → memory)
   - Planner: chooses intent and format from instruction, conversation, context
   - Classify: intent classification with a label from a list
   - Generate: document generation with instruction, conversation, context

3. **Structured outputs**:
   - JSON schemas for planner, classify, generate
   - Action templates in `actions/*.json`, format configs in `formats/*.json`
   - Scaleway supports `response_format` with `json_schema`

### Architecture

The library uses a provider-based architecture built on ProviderKit:

- Each AI service is implemented as a provider inheriting from `AIProviderBase`
- `AIProviderBase` extends `ProviderBase` from ProviderKit
- Providers are organized in the `providers/` directory
- Common functionality is shared through the base `AIProviderBase` class
- Provider discovery and management is handled by ProviderKit

### Available Services

Providers implement services such as:

- **`prompt`**: Agent loop — plan (intent + format) → execute → memory
- **`planner`**: Choose intent and output format from instruction, conversation, context
- **`classify`**: Intent classification with labels (returns one of the provided labels)
- **`generate`**: Document generation based on instruction, conversation history, and context

### Supported Providers

- **OpenAI** – GPT models
- **Anthropic** – Claude models
- **Google** – Gemini models
- **Mistral** – Mistral models
- **Meta** – Llama models
- **Scaleway** – Generative APIs (Llama, Mistral, Qwen, Pixtral, etc.)

### Use Cases

- Multi-provider AI orchestration
- Intent classification and routing
- Document generation with context
- Fallback across providers when one fails
- Unified API across different LLM backends
