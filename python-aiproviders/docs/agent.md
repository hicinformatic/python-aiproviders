# Agent Architecture

This document describes how the AI agent works: planner, execution loop, formats, schemas, and actions.

## Flow Diagram

```mermaid
flowchart TB
    subgraph Input
        INST[instruction]
        CONV[conversation]
        CTX[context]
    end

    subgraph Agent Loop["prompt() - Agent Loop"]
        direction TB
        PLAN[plan]
        EXEC[execute]
        MEM[memory]
        CHECK{result.next?}

        INST --> PLAN
        CONV --> PLAN
        CTX --> PLAN

        PLAN --> |intent, format| EXEC
        INST --> EXEC
        CONV --> EXEC
        CTX --> EXEC

        EXEC --> MEM
        MEM --> CHECK
        CHECK -->|oui| PLAN
        CHECK -->|non| OUT[return result]
    end

    subgraph Planner["plan() - LLM Call"]
        direction TB
        P_IN[instruction, conversation, context]
        P_CFG[intents, formats, formats_descriptions]
        P_LLM[run_llm_provider planner]
        P_OUT[intent, format, confidence]

        P_IN --> P_LLM
        P_CFG --> P_LLM
        P_LLM --> P_OUT
    end

    subgraph Execute["execute() - LLM or Tool"]
        direction TB
        E_IN[intent, instruction, conversation, context]
        E_FMT[output_type]
        E_CHK{intent in tools?}
        E_TOOL[run_tool]
        E_LLM[run_llm_provider intent]

        E_IN --> E_CHK
        E_FMT --> E_LLM
        E_CHK -->|oui| E_TOOL
        E_CHK -->|non| E_LLM
    end

    subgraph Provider["run_llm_provider - Scaleway"]
        direction TB
        R_PAY[payload: type, instruction, conversation, context, output_type...]
        R_DISP{type?}
        R_PLAN[scaleway_planner]
        R_GEN[scaleway_generate]
        R_CLS[scaleway_classify]
        R_GEN2[_chat_completion_generic]

        R_PAY --> R_DISP
        R_DISP -->|planner| R_PLAN
        R_DISP -->|generate| R_GEN
        R_DISP -->|classify| R_CLS
        R_DISP -->|extract, summarize...| R_GEN2
    end

    subgraph ActionTemplate["actions/*.json"]
        direction LR
        A_PLAN[planner.json]
        A_GEN[generate.json]
        A_CLS[classify.json]
        A_OTH[extract, translate...]
    end

    subgraph FormatConfig["formats/*.json"]
        direction LR
        F_JSON[json]
        F_HTML[html]
        F_TEXT[text]
        F_XML[xml]
        F_CSV[csv]
    end

    subgraph Schemas["schemas/*.json"]
        direction LR
        S_PLAN[planner.schema]
        S_GEN[generate.schema]
        S_CLS[classify.schema]
        S_BASE[base_action.schema]
    end

    R_PLAN --> A_PLAN
    R_GEN --> A_GEN
    R_CLS --> A_CLS
    R_GEN2 --> A_OTH

    R_PLAN --> F_JSON
    R_GEN --> F_JSON
    R_GEN --> F_HTML
    R_GEN --> F_TEXT

    R_PLAN --> S_PLAN
    R_GEN --> S_GEN
    R_CLS --> S_CLS
    R_GEN2 --> S_BASE
```

## Components

### 1. prompt() — Agent Loop

Entry point. For each step (max 8):

1. **plan** — Chooses intent + format from instruction, conversation, context
2. **execute** — Runs the intent (LLM or registered tool)
3. **memory** — Records step in history
4. **next** — If `result.next` exists, continues loop with that instruction; else returns

### 2. plan() — Planner

Calls `run_llm_provider` with `type: "planner"`. Provides:

- `instruction`, `conversation`, `context` — For format choice (e.g. context.input=richtext → html)
- `intents` — Available actions (extract, generate, classify, chat, etc.)
- `formats` — json, xml, csv, html, text
- `formats_descriptions` — Descriptions from `formats/*.json` (helps choose richtext → html)

Returns `{intent, format, confidence}`. If confidence < 0.6, falls back to `chat` + `json`.

### 3. execute() — Executor

- If intent is a **registered tool** → `run_tool()`
- Else → `run_llm_provider` with `type: intent`, `output_type: format`

### 4. run_llm_provider — Provider Dispatch

Routes by `type`:

- `planner` → `scaleway_planner` (schema with intents/formats enums)
- `generate` → `scaleway_generate` (schema from `generate.schema` + format)
- `classify` → `scaleway_classify` (schema with labels enum)
- Other intents → `_chat_completion_generic` (uses `{intent}.schema` or `base_action.schema`)

Accumulates usage (input_tokens, output_tokens, cost) per call.

### 5. actions/

Templates for prompts: `{{instruction}}`, `{{conversation}}`, `{{context}}`, etc.

- `planner.json` — Chooses intent and format
- `generate.json` — Document generation
- `classify.json` — Intent classification
- `extract.json`, `translate.json`, etc. — Generic intents

### 6. formats/

Output type configs: `description`, `instruction` (appended to system prompt), `parse`, `content_type`.

- `json` — Structured JSON (schema-enforced for Scaleway)
- `html` — HTML for emails, rich content
- `text` — Plain text
- `xml`, `csv` — Structured formats

### 7. schemas/

JSON schemas for structured output:

- `planner.schema.json` — intent (enum), format (enum), confidence
- `generate.schema.json` — content, next
- `classify.schema` — classify (enum), confidence
- `base_action.schema.json` — Fallback for generic intents
