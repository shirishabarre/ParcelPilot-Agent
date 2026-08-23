import asyncio
import json
from contextlib import AsyncExitStack
from dataclasses import dataclass, field

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from auth import Session
from config import ACTION_TOOL_NAMES, MAX_TOOL_HOPS_PER_TURN, MCP_SERVERS
from llm_client import get_llm_client
from observability import langfuse, is_enabled, flush

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
    pending_action: dict | None = None
    trace_id: str | None = None

def _load_prompt(role: str, session: Session) -> str:
    fname = "system_prompt_customer.md" if role == "customer" else "system_prompt_internal.md"
    with open(f"{PROMPTS_DIR}/{fname}", encoding="utf-8") as f:
        text = f.read()
    return text.format(
        account_id=session.account_id or "",
        account_name=session.account_id or "",
        display_name=session.display_name,
    )

class Orchestrator:
    def __init__(self):
        self._stack = AsyncExitStack()
        self.sessions: dict[str, ClientSession] = {}
        self.tool_owner: dict[str, str] = {}
        self.tool_specs: list[dict] = []
        self.llm = get_llm_client()

    async def connect(self):
        for key, cfg in MCP_SERVERS.items():
            params = StdioServerParameters(
                command=cfg["command"][0],
                args=cfg["command"][1:]
            )
            read, write = await self._stack.enter_async_context(
                stdio_client(params)
            )
            session = await self._stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            self.sessions[key] = session

            listed = await session.list_tools()

            for tool in listed.tools:
                self.tool_owner[tool.name] = key
                self.tool_specs.append({
                    "name": tool.name,
                    "description": tool.description or "",
                    "input_schema": tool.inputSchema,
                })

    async def aclose(self):
        await self._stack.aclose()

    def _inject_scope(
        self,
        tool_name: str,
        args: dict,
        session: Session
    ) -> dict:
        args = dict(args)

        if (
            "caller_role" in args
            or tool_name in ACTION_TOOL_NAMES
            or self.tool_owner.get(tool_name) in ("data", "actions")
        ):
            args["caller_role"] = session.role
            args["caller_account_id"] = session.account_id or ""

        if tool_name == "search_documents" and session.role == "customer":
            args["account_scope"] = session.account_id or ""

        if tool_name in ACTION_TOOL_NAMES:
            args["confirmed"] = False

        return args

    async def _call_tool(self, name: str, args: dict):
        server_key = self.tool_owner[name]

        result = await self.sessions[server_key].call_tool(
            name,
            args
        )

        text_parts = [
            c.text
            for c in result.content
            if getattr(c, "text", None)
        ]

        raw = "\n".join(text_parts)

        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            parsed = raw

        return server_key, parsed

    def _start_trace(self, session: Session, user_text: str):
        if not is_enabled():
            return None

        return langfuse.start_as_current_observation(
            as_type="agent",
            name="parcelpilot-agent",
            input={
                "user_message": user_text
            },
            metadata={
                "application": "parcelpilot",
                "role": session.role,
                "account_id": session.account_id or "all_accounts",
                "user_id": session.user_id,
            },
        )

    async def run_turn(
        self,
        session: Session,
        history: list[dict],
        user_text: str
    ) -> TurnResult:

        system_prompt = _load_prompt(session.role, session)

        messages = list(history) + [
            {
                "role": "user",
                "content": user_text
            }
        ]

        trace_entries: list[ToolTraceEntry] = []
        pending_action = None
        final_reply = ""
        trace_id = None

        if not is_enabled():
            return await self._run_turn_without_observability(
                session,
                history,
                user_text
            )

        with self._start_trace(session, user_text) as agent_observation:

            trace_id = agent_observation.trace_id

            try:
                for hop in range(MAX_TOOL_HOPS_PER_TURN):

                    with agent_observation.start_as_current_observation(
                        as_type="generation",
                        name="llm-decision",
                        model=getattr(
                            self.llm,
                            "model",
                            "configured-llm"
                        ),
                        input={
                            "messages": messages,
                            "tool_count": len(self.tool_specs),
                            "hop": hop + 1,
                        },
                    ) as generation:

                        resp = self.llm.chat(
                            system_prompt,
                            messages,
                            self.tool_specs
                        )

                        generation.update(
                            output={
                                "text": resp.text,
                                "tool_calls": [
                                    {
                                        "name": call.name,
                                        "arguments": call.arguments
                                    }
                                    for call in resp.tool_calls
                                ]
                            }
                        )

                    if not resp.tool_calls:

                        final_reply = resp.text

                        agent_observation.update(
                            output={
                                "reply": final_reply,
                                "tool_calls": len(trace_entries),
                                "status": "completed"
                            }
                        )

                        return TurnResult(
                            reply=final_reply,
                            tool_trace=trace_entries,
                            pending_action=pending_action,
                            trace_id=trace_id
                        )

                    messages.append({
                        "role": "assistant",
                        "content": resp.text or "(calling tools)"
                    })

                    for call in resp.tool_calls:

                        scoped_args = self._inject_scope(
                            call.name,
                            call.arguments,
                            session
                        )

                        server_key = self.tool_owner.get(
                            call.name,
                            "unknown"
                        )

                        with agent_observation.start_as_current_observation(
                            as_type="tool",
                            name=f"mcp:{call.name}",
                            input={
                                "server": server_key,
                                "tool": call.name,
                                "arguments": scoped_args
                            },
                        ) as tool_observation:

                            try:
                                server_key, result = await self._call_tool(
                                    call.name,
                                    scoped_args
                                )

                                tool_observation.update(
                                    output=result
                                )

                            except Exception as exc:

                                tool_observation.update(
                                    output={
                                        "error": str(exc),
                                        "status": "failed"
                                    }
                                )

                                raise

                        trace_entries.append(
                            ToolTraceEntry(
                                server=server_key,
                                tool=call.name,
                                arguments=scoped_args,
                                result=result
                            )
                        )

                        if call.name == "search_documents":

                            if isinstance(result, list):

                                documents = result

                                for index, document in enumerate(
                                    documents[:10]
                                ):

                                    with agent_observation.start_as_current_observation(
                                        as_type="retriever",
                                        name="rag-document",
                                        input={
                                            "rank": index + 1,
                                            "query": scoped_args.get(
                                                "query",
                                                ""
                                            )
                                        },
                                    ) as retrieval_observation:

                                        retrieval_observation.update(
                                            output=document
                                        )

                        if (
                            call.name in ACTION_TOOL_NAMES
                            and isinstance(result, dict)
                            and result.get("status") == "PREVIEW_ONLY"
                        ):

                            pending_action = {
                                "tool": call.name,
                                "arguments": scoped_args,
                                "preview": result
                            }

                        messages.append({
                            "role": "user",
                            "content": (
                                f"[Tool result for {call.name}]: "
                                f"{json.dumps(result, default=str)}"
                            ),
                        })

                final_reply = (
                    "I've gathered information across several tools "
                    "but need to stop here — please rephrase or ask "
                    "a more specific follow-up."
                )

                agent_observation.update(
                    output={
                        "reply": final_reply,
                        "tool_calls": len(trace_entries),
                        "status": "max_tool_hops"
                    }
                )

                return TurnResult(
                    reply=final_reply,
                    tool_trace=trace_entries,
                    pending_action=pending_action,
                    trace_id=trace_id
                )

            except Exception as exc:

                agent_observation.update(
                    output={
                        "status": "error",
                        "error": str(exc)
                    }
                )

                raise

            finally:
                flush()

    async def _run_turn_without_observability(
        self,
        session: Session,
        history: list[dict],
        user_text: str
    ) -> TurnResult:

        system_prompt = _load_prompt(
            session.role,
            session
        )

        messages = list(history) + [
            {
                "role": "user",
                "content": user_text
            }
        ]

        trace_entries = []
        pending_action = None

        for _ in range(MAX_TOOL_HOPS_PER_TURN):

            resp = self.llm.chat(
                system_prompt,
                messages,
                self.tool_specs
            )

            if not resp.tool_calls:

                return TurnResult(
                    reply=resp.text,
                    tool_trace=trace_entries,
                    pending_action=pending_action
                )

            messages.append({
                "role": "assistant",
                "content": resp.text or "(calling tools)"
            })

            for call in resp.tool_calls:

                scoped_args = self._inject_scope(
                    call.name,
                    call.arguments,
                    session
                )

                server_key, result = await self._call_tool(
                    call.name,
                    scoped_args
                )

                trace_entries.append(
                    ToolTraceEntry(
                        server=server_key,
                        tool=call.name,
                        arguments=scoped_args,
                        result=result
                    )
                )

                if (
                    call.name in ACTION_TOOL_NAMES
                    and isinstance(result, dict)
                    and result.get("status") == "PREVIEW_ONLY"
                ):

                    pending_action = {
                        "tool": call.name,
                        "arguments": scoped_args,
                        "preview": result
                    }

                messages.append({
                    "role": "user",
                    "content": (
                        f"[Tool result for {call.name}]: "
                        f"{json.dumps(result, default=str)}"
                    )
                })

        return TurnResult(
            reply=(
                "I've gathered information across several tools "
                "but need to stop here — please rephrase or ask "
                "a more specific follow-up."
            ),
            tool_trace=trace_entries,
            pending_action=pending_action
        )

    async def execute_confirmed_action(
        self,
        pending_action: dict
    ) -> dict:

        tool_name = pending_action["tool"]

        args = dict(
            pending_action["arguments"]
        )

        args["confirmed"] = True

        if is_enabled():

            with langfuse.start_as_current_observation(
                as_type="tool",
                name=f"confirmed-action:{tool_name}",
                input={
                    "tool": tool_name,
                    "arguments": args
                },
            ) as action_observation:

                try:

                    server_key, result = await self._call_tool(
                        tool_name,
                        args
                    )

                    action_observation.update(
                        output={
                            "server": server_key,
                            "result": result,
                            "confirmed": True
                        }
                    )

                    return result

                except Exception as exc:

                    action_observation.update(
                        output={
                            "status": "error",
                            "error": str(exc)
                        }
                    )

                    raise

                finally:
                    flush()

        _, result = await self._call_tool(
            tool_name,
            args
        )

        return result

async def _self_test():

    orch = Orchestrator()

    await orch.connect()

    print("Connected. Tools discovered:")

    for name, owner in orch.tool_owner.items():
        print(
            f"  [{owner}] {name}"
        )

    from auth import login

    staff = login("rohit")

    args = orch._inject_scope(
        "create_escalation",
        {
            "account_id": "ACCT-001",
            "reason": "test",
            "severity": "P2",
            "ticket_id": "TKT-501",
            "caller_role": "customer",
            "caller_account_id": "SOMETHING_ELSE",
        },
        staff
    )

    print(
        "\nInjected args "
        "(should show caller_role=staff, confirmed=False):",
        args
    )

    _, result = await orch._call_tool(
        "create_escalation",
        args
    )

    print(
        "Preview-only result:",
        result
    )

    await orch.aclose()

if __name__ == "__main__":
    asyncio.run(_self_test())
