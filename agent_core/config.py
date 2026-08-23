"""Central config: paths and which MCP server owns which tool (used by the
orchestrator to route calls and by the UI to label the tool badge)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MCP_SERVERS = {
    "docs": {
        "label": "Document Search",
        "command": ["python3", str(ROOT / "mcp_servers" / "docs_server" / "server.py")],
    },
    "data": {
        "label": "Data Lookup / Calculation",
        "command": ["python3", str(ROOT / "mcp_servers" / "data_server" / "server.py")],
    },
    "actions": {
        "label": "Action (writes / escalations)",
        "command": ["python3", str(ROOT / "mcp_servers" / "actions_server" / "server.py")],
    },
}

# Tools that mutate state — the orchestrator always requires a confirmed round-trip for these.
ACTION_TOOL_NAMES = {"create_escalation", "update_ticket_status", "create_followup_task"}

MAX_TOOL_HOPS_PER_TURN = 8  # guard against infinite tool loops
