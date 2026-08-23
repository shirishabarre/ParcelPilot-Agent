"""
Thin wrapper so orchestrator.py can call either free-tier provider through
one interface: chat(messages, tools) -> response with text and/or tool_calls.

Both providers are free tier:
  - Gemini: https://aistudio.google.com/apikey  (GEMINI_API_KEY)
  - Groq:   https://console.groq.com/keys        (GROQ_API_KEY)
"""
import json
import os
from dataclasses import dataclass, field


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class LLMResponse:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)


def _mcp_tools_to_gemini_schema(tool_specs: list[dict]) -> list[dict]:
    """tool_specs: [{name, description, input_schema}] -> Gemini function-declaration format."""
    return [{
        "name": t["name"],
        "description": t["description"],
        "parameters": t["input_schema"],
    } for t in tool_specs]


class GeminiClient:
    def __init__(self, model: str | None = None):
        from google import genai
        self.genai = genai
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self.model = model or os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

    def chat(self, system_prompt: str, messages: list[dict], tool_specs: list[dict]) -> LLMResponse:
        from google.genai import types
        contents = []
        for m in messages:
            role = "model" if m["role"] == "assistant" else "user"
            contents.append(types.Content(role=role, parts=[types.Part(text=m["content"])]))

        tools = [types.Tool(function_declarations=_mcp_tools_to_gemini_schema(tool_specs))] if tool_specs else None
        config = types.GenerateContentConfig(system_instruction=system_prompt, tools=tools)

        resp = self.client.models.generate_content(model=self.model, contents=contents, config=config)
        out = LLMResponse()
        cand = resp.candidates[0] if resp.candidates else None
        if not cand:
            return out
        for part in cand.content.parts:
            if getattr(part, "text", None):
                out.text += part.text
            fc = getattr(part, "function_call", None)
            if fc:
                out.tool_calls.append(ToolCall(id=fc.name, name=fc.name, arguments=dict(fc.args or {})))
        return out


class GroqClient:
    def __init__(self, model: str | None = None):
        from groq import Groq
        self.client = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.model = model or os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

    def chat(self, system_prompt: str, messages: list[dict], tool_specs: list[dict]) -> LLMResponse:
        tools = [{
            "type": "function",
            "function": {"name": t["name"], "description": t["description"], "parameters": t["input_schema"]},
        } for t in tool_specs]

        full_messages = [{"role": "system", "content": system_prompt}] + messages
        resp = self.client.chat.completions.create(
            model=self.model, messages=full_messages, tools=tools or None,
        )
        choice = resp.choices[0].message
        out = LLMResponse(text=choice.content or "")
        for tc in (choice.tool_calls or []):
            out.tool_calls.append(ToolCall(
                id=tc.id, name=tc.function.name, arguments=json.loads(tc.function.arguments or "{}"),
            ))
        return out


def get_llm_client():
    provider = os.environ.get("LLM_PROVIDER", "gemini").lower()
    if provider == "groq":
        return GroqClient()
    return GeminiClient()
