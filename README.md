# AIProviders

Monorepo contenant **aiproviders** (bibliothèque Python pour les fournisseurs IA) et **django-aiproviders** (intégration Django).

## Packages

### aiproviders — `python-aiproviders/`

Bibliothèque Python pour la gestion des fournisseurs d'IA. Interface unifiée vers plusieurs providers (OpenAI, Anthropic, Google, Mistral, Meta, Scaleway) via ProviderKit.

- **Providers** : OpenAI, Anthropic, Google Gemini, Mistral, Meta Llama, Scaleway
- **Services** : prompt, generate, classify, run_llm_provider
- **CLI** : `aiproviders prompt --instruction "..."`, `aiproviders provider --list`

📁 Détails : [python-aiproviders/README.md](python-aiproviders/README.md) | Docs : [python-aiproviders/docs/](python-aiproviders/docs/)

### django-aiproviders — `django-aiproviders/`

Intégration Django pour AIProviders.

📁 Docs : [django-aiproviders/docs/](django-aiproviders/docs/)

## Structure du dépôt

```
aiproviders/
├── python-aiproviders/   # Bibliothèque core
├── django-aiproviders/   # Intégration Django
└── README.md
```

## Développement

Chaque package a son propre `service.py` :

```bash
# Dans python-aiproviders/ ou django-aiproviders/
./service.py dev install-dev
./service.py dev test
./service.py quality lint
```

## Licence

MIT
