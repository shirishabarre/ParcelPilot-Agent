"""
The agent orchestrator: an MCP CLIENT that connects to the three MCP
SERVERS (docs, data, actions) over stdio, exposes their tools to the LLM,
and runs the tool-use loop.

Critical security property: caller_role / caller_account_id passed into
every data/action tool call are OVERWRITTEN here with the authenticated
session's real values before dispatch — never taken from whatever the model
put in its tool-call arguments. This is what makes access control enforced
"in the tool layer" rather than relying on the model behaving.

Critical safety property: any tool in config.ACTION_TOOL_NAMES is ALWAYS
invoked with confirmed=False when triggered by the model. A real
confirmed=True execution only happens via execute_confirmed_action(),
called by the UI after the human clicks "Confirm" on the exact preview
shown — the model can never silently flip confirmed=True itself.
"""
import asyncio
import json
from contextlib import AsyncExitStack
from dataclasses import dataclass, field

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from auth import Session
from config import ACTION_TOOL_NAMES, MAX_TOOL_HOPS_PER_TURN, MCP_SERVERS
from llm_client import get_llm_client

PROMPTS_DIR = __file__.rsplit("/", 1)[0] + "/prompts"


@dataclass
class ToolTraceEntry:
    server: str
    tool: str
    arguments: dict
    result: object


@dataclass
class TurnResult:
    reply: str
    tool_trace: list[ToolTraceEntry] = field(default_factory=list)
    pending_action: dict | None = None  # set when an action tool returned PREVIEW_ONLY


def _load_prompt(role: str, session: Session) -> str:
    fname = "system_prompt_customer.md" if role == "customer" else "system_prompt_internal.md"
    with open(f"{PROMPTS_DIR}/{fname}") as f:
        text = f.read()
    return text.format(
        account_id=session.account_id or "", account_name=session.account_id or "",
        display_name=session.display_name,
    )


class Orchestrator:
    def __init__(self):
        self._stack = AsyncExitStack()
        self.sessions: dict[str, ClientSession] = {}
        self.tool_owner: dict[str, str] = {}   # tool_name -> server_key
        self.tool_specs: list[dict] = []        # [{name, description, input_schema}] for the LLM
        self.llm = get_llm_client()

    async def connect(self):
        for key, cfg in MCP_SERVERS.items():
            params = StdioServerParameters(command=cfg["command"][0], args=cfg["command"][1:])
            read, write = await self._stack.enter_async_context(stdio_client(params))
            session = await self._stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            self.sessions[key] = session

            listed = await session.list_tools()
            for t in listed.tools:
                self.tool_owner[t.name] = key
                self.tool_specs.append({
                    "name": t.name,
                    "description": t.description or "",
                    "input_schema": t.inputSchema,
                })

    async def aclose(self):
        await self._stack.aclose()

    def _inject_scope(self, tool_name: str, args: dict, session: Session) -> dict:
        args = dict(args)
        # Data + action tools: always overwrite with the real session, never trust the model.
        if "caller_role" in args or tool_name in ACTION_TOOL_NAMES or self.tool_owner.get(tool_name) in ("data", "actions"):
            args["caller_role"] = session.role
            args["caller_account_id"] = session.account_id or ""
        # Docs tool: a customer's search is always scoped to their own account; staff may pass through.
        if tool_name == "search_documents" and session.role == "customer":
            args["account_scope"] = session.account_id or ""
        # Never let the model self-confirm a state-changing action.
        if tool_name in ACTION_TOOL_NAMES:
            args["confirmed"] = False
        return args

    async def _call_tool(self, name: str, args: dict):
        server_key = self.tool_owner[name]
        result = await self.sessions[server_key].call_tool(name, args)
        # MCP tool results come back as content blocks; our tools return JSON-able Python objects
        # serialized as text by FastMCP -> parse back to a dict/list for the trace + LLM.
        text_parts = [c.text for c in result.content if getattr(c, "text", None)]
        raw = "\n".join(text_parts)
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            parsed = raw
        return server_key, parsed

    async def run_turn(self, session: Session, history: list[dict], user_text: str) -> TurnResult:
        system_prompt = _load_prompt(session.role, session)
        messages = list(history) + [{"role": "user", "content": user_text}]
        trace: list[ToolTraceEntry] = []
        pending_action = None

        for _ in range(MAX_TOOL_HOPS_PER_TURN):
            resp = self.llm.chat(system_prompt, messages, self.tool_specs)

            if not resp.tool_calls:
                return TurnResult(reply=resp.text, tool_trace=trace, pending_action=pending_action)

            # Record the assistant's tool-call turn, then execute each and feed results back.
            messages.append({"role": "assistant", "content": resp.text or "(calling tools)"})
            for call in resp.tool_calls:
                scoped_args = self._inject_scope(call.name, call.arguments, session)
                server_key, result = await self._call_tool(call.name, scoped_args)
                trace.append(ToolTraceEntry(server=server_key, tool=call.name, arguments=scoped_args, result=result))

                if call.name in ACTION_TOOL_NAMES and isinstance(result, dict) and result.get("status") == "PREVIEW_ONLY":
                    pending_action = {"tool": call.name, "arguments": scoped_args, "preview": result}

                messages.append({
                    "role": "user",
                    "content": f"[Tool result for {call.name}]: {json.dumps(result, default=str)}",
                })

        return TurnResult(reply="I've gathered information across several tools but need to stop here — "
                                 "please rephrase or ask a more specific follow-up.",
                           tool_trace=trace, pending_action=pending_action)

    async def execute_confirmed_action(self, pending_action: dict) -> dict:
        """Called only after the human clicks Confirm in the UI. Re-invokes the
        exact same tool + arguments captured in the preview, with confirmed=True."""
        tool_name = pending_action["tool"]
        args = dict(pending_action["arguments"])
        args["confirmed"] = True
        server_key, result = await self._call_tool(tool_name, args)
        return result


async def _self_test():
    """Smoke-test the MCP plumbing without needing an LLM key."""
    orch = Orchestrator()
    await orch.connect()
    print("Connected. Tools discovered:")
    for name, owner in orch.tool_owner.items():
        print(f"  [{owner}] {name}")

    from auth import login
    staff = login("rohit")
    args = orch._inject_scope("create_escalation", {
        "account_id": "ACCT-001", "reason": "test", "severity": "P2", "ticket_id": "TKT-501",
        "caller_role": "customer", "caller_account_id": "SOMETHING_ELSE",  # model trying to lie -> must be overwritten
    }, staff)
    print("\nInjected args (should show caller_role=staff, confirmed=False):", args)
    _, result = await orch._call_tool("create_escalation", args)
    print("Preview-only result:", result)

    await orch.aclose()


if __name__ == "__main__":
    asyncio.run(_self_test())
