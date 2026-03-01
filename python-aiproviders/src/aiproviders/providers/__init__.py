from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional

from providerkit.providers.base import ProviderBase


@lru_cache(maxsize=32)
def _load_json(folder: str, name: str) -> Dict[str, Any]:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, folder, f"{name}.json")
    with open(path, encoding="utf-8") as file:
        return json.load(file)


class AIProviderBase(ProviderBase):
    CONFIDENCE_THRESHOLD = 0.6

    _default_services_cfg = {
        "prompt": {"label": "Prompt", "description": "Prompt", "fields": {
            "result": {"label": "Result", "description": "Result", "format": "dict[str, Any]"},
        }},
        "run_llm_provider": {"label": "Run LLM Provider", "description": "Run LLM Provider", "fields": {
            "result": {"label": "Result", "description": "Result", "format": "dict[str, Any]"},
        }},
        "get_models": {"label": "Get Models", "description": "List LLM models", "fields": {
            "id": {"label": "ID", "description": "Model ID", "format": "str"},
            "object": {"label": "Object", "description": "Object type", "format": "str"},
            "owner": {"label": "Owner", "description": "Model owner", "format": "str"},
            "created_at": {"label": "Created At", "description": "Created timestamp", "format": "str"},
            "default": {"label": "Default", "description": "Default model marker", "format": "str"},
        }},
    }
    ai_actions = {
        "extract": {"label": "Extract", "description": "Extract"},
        "generate": {"label": "Generate", "description": "Generate"},
        "summarize": {"label": "Summarize", "description": "Summarize"},
        "translate": {"label": "Translate", "description": "Translate"},
        "classify": {"label": "Classify", "description": "Classify"},
        "analyze": {"label": "Analyze", "description": "Analyze"},
        "detect": {"label": "Detect", "description": "Detect"},
        "verify": {"label": "Verify", "description": "Verify"},
        "validate": {"label": "Validate", "description": "Validate"},
        "enhance": {"label": "Enhance", "description": "Enhance"},
        "optimize": {"label": "Optimize", "description": "Optimize"},
        "chat": {"label": "Chat", "description": "Chat"},
        "action": {"label": "Action", "description": "Action"},
    }
    ai_fields = {
        "instruction": {"label": "Instruction", "description": "Instruction", "format": "str"},
        "conversation": {"label": "Conversation", "description": "Conversation", "format": "list[dict[str, Any]]"},
        "context": {"label": "Context", "description": "Context", "format": "dict[str, Any]"},
        "next": {"label": "Next Instruction", "description": "Next Instruction", "format": "str"},
    }

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._memory: Dict[str, Any] = {
            "history": [],
            "state": {},
        }
        self._usage: Dict[str, Any] = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "steps": [],
        }
        self.tools: Dict[str, Callable[..., Any]] = {}

    # ==========================
    # FORMAT / SCHEMA
    # ==========================

    @property
    def models(self) -> List[Dict[str, Any]]:
        """Fetch available models from provider."""
        return self.get_models()

    def get_models(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """Fetch available models from provider."""
        return []

    def get_action(self, action_name: str) -> Dict[str, Any]:
        """Load action template (prompt) from actions/."""
        return _load_json("actions", action_name).copy()

    def get_action_template(self, action_name: str, output_type: str = "json") -> Dict[str, str]:
        """Load action + format instruction from formats/. All actions support all formats."""
        action = self.get_action(action_name)
        system = action.get("system", "")
        user = action.get("user", "")
        fmt_config = self.get_output_type(output_type)
        format_instruction = fmt_config.get("instruction", "")
        if format_instruction:
            system = f"{system} {format_instruction}".strip()
        return {"system": system, "user": user}

    def get_output_type(self, output_type: str) -> Dict[str, Any]:
        """Load response type config (json, xml, csv, html, text) from formats/."""
        return _load_json("formats", output_type)

    def get_schema(self, schema_name: str) -> Dict[str, Any]:
        return _load_json("schemas", schema_name)

    def get_combined_schema(self, action: str, output_type: str) -> Dict[str, Any]:
        """Load schema for action+format. Falls back to action schema for json."""
        combined = f"{action}.{output_type}"
        try:
            return _load_json("schemas", combined).copy()
        except FileNotFoundError:
            pass
        if output_type == "json":
            return _load_json("schemas", f"{action}.schema").copy()
        return _load_json("schemas", "base_action.schema").copy()

    @property
    def available_intents(self) -> List[str]:
        return list(self.ai_actions.keys())

    @property
    def available_formats(self) -> List[str]:
        """Formats from formats/ folder: json, xml, csv, html, text."""
        return ["json", "xml", "csv", "html", "text"]

    def get_formats_descriptions(self) -> str:
        """Format names with descriptions to help planner choose (e.g. richtext context → html)."""
        parts = []
        for name in self.available_formats:
            cfg = self.get_output_type(name)
            desc = cfg.get("description", name)
            parts.append(f"{name}: {desc}")
        return "; ".join(parts)

    # ==========================
    # REQUEST WRAPPER (usage tracking)
    # ==========================

    def _accumulate_usage(self, usage: Dict[str, Any], intent: str = "request") -> None:
        """Add usage to totals and append step."""
        if not usage:
            return
        inp = usage.get("input_tokens") or usage.get("prompt_tokens", 0)
        out = usage.get("output_tokens") or usage.get("completion_tokens", 0)
        total = usage.get("total_tokens") or (inp + out)
        cost = float(usage.get("total_cost", 0.0))
        self._usage["input_tokens"] += inp
        self._usage["output_tokens"] += out
        self._usage["total_tokens"] += total
        self._usage["total_cost"] += cost
        self._usage["steps"].append({
            "intent": intent,
            "input_tokens": inp,
            "output_tokens": out,
            "total_tokens": total,
            "cost": cost,
        })

    def run_llm_provider(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch to provider impl and accumulate usage from each response."""
        intent = payload.get("type", "request")
        payload_copy = {**payload}
        response = self._run_llm_provider_impl(payload_copy)
        usage = response.get("usage", {}) if isinstance(response, dict) else {}
        self._accumulate_usage(usage, intent=intent)
        return response

    def _run_llm_provider_impl(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Provider-specific LLM call. Override in subclasses (e.g. Scaleway)."""
        raise NotImplementedError

    # ==========================
    # PLANNER
    # ==========================

    def plan(
        self,
        instruction: str,
        conversation: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Plan intent + format based on instruction, context and conversation. Falls back to chat+json if confidence low."""
        result = self.run_llm_provider({
            "type": "planner",
            "instruction": instruction,
            "conversation": conversation,
            "context": context,
            "intents": self.available_intents,
            "formats": self.available_formats,
            "formats_descriptions": self.get_formats_descriptions(),
        })
        intent = result.get("intent", "generate")
        output_type = result.get("format", "json")
        confidence = result.get("confidence", 1.0)
        if confidence < self.CONFIDENCE_THRESHOLD:
            return {"intent": "chat", "format": "json", "confidence": confidence}
        return {"intent": intent, "format": output_type, "confidence": confidence, **result}

    # ==========================
    # EXECUTOR
    # ==========================

    def execute(
        self,
        intent: str,
        instruction: str,
        conversation: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
        output_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute intent with output_type. Uses run_llm_provider() → provider+model."""
        output_type = output_type or "json"
        if intent in self.tools:
            return self.run_tool(intent, instruction)
        result = self.run_llm_provider({
            "type": intent,
            "instruction": instruction,
            "conversation": conversation,
            "context": context,
            "output_type": output_type,
        })
        return result if isinstance(result, dict) else {"result": result}

    # ==========================
    # TOOL SYSTEM
    # ==========================

    def register_tool(self, name: str, func: Callable[..., Any]) -> None:
        self.tools[name] = func

    def run_tool(self, name: str, instruction: str) -> Dict[str, Any]:
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")
        result = self.tools[name](instruction)
        return result if isinstance(result, dict) else {"result": result}

    # ==========================
    # AGENT LOOP
    # ==========================

    def prompt(
        self,
        instruction: Optional[str] = None,
        conversation: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
        max_steps: int = 8,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Agent loop: plan -> execute -> memory -> next or stop."""
        instruction = instruction or kwargs.get("instruction", "")
        steps: List[Dict[str, Any]] = []
        current_instruction = instruction

        for step in range(max_steps):
            plan = self.plan(current_instruction, conversation=conversation, context=context)
            intent = plan.get("intent", "generate")
            output_type = plan.get("format", "json")

            result = self.execute(
                intent=intent,
                instruction=current_instruction,
                conversation=conversation,
                context=context,
                output_type=output_type,
            )

            self._memory["history"].append({
                "intent": intent,
                "format": output_type,
                "instruction": current_instruction,
                "result": result,
            })

            steps.append({
                "step": step + 1,
                "intent": intent,
                "format": output_type,
                "result": result,
            })

            next_instruction = result.get("next") if isinstance(result, dict) else None
            if not next_instruction:
                return {
                    "result": result,
                    "steps": steps,
                    "memory": self._memory,
                    "usage": self._usage,
                }

            current_instruction = next_instruction

        raise RuntimeError("Max steps reached")

