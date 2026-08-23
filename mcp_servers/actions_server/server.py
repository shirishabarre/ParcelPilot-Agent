"""
MCP Server: actions_server
Tool 3 of 3 (State-changing action, mocked) — creates escalations, updates
ticket status, creates follow-up tasks.

CONFIRMATION CONTRACT: every tool takes confirmed: bool.
  - confirmed=False (default) -> returns a PREVIEW ONLY. Nothing is written.
  - confirmed=True  -> writes the action and returns a receipt.
The orchestrator must show the preview to the human and only re-call with
confirmed=True after the user explicitly approves — this is enforced here
so it can't be skipped even if the model tries to.

Run standalone for debugging:  python mcp_servers/actions_server/server.py
"""
import json

from mcp.server.fastmcp import FastMCP

from store import list_actions, log_action

mcp = FastMCP("parcelpilot-actions")


@mcp.tool()
def create_escalation(account_id: str, caller_role: str, reason: str, severity: str,
                       order_id: str = "", ticket_id: str = "", confirmed: bool = False) -> dict:
    """
    Escalate an issue to a human on the support/ops team.
    severity: 'P1' | 'P2' | 'P3'.
    Set confirmed=True only after the user has explicitly approved the
    preview shown to them; confirmed=False (default) only returns a preview
    and writes nothing.
    """
    if caller_role not in ("staff", "customer"):
        return {"error": "invalid caller_role"}
    preview = {
        "action": "create_escalation", "account_id": account_id, "order_id": order_id,
        "ticket_id": ticket_id, "severity": severity, "reason": reason,
    }
    if not confirmed:
        return {"status": "PREVIEW_ONLY", "would_create": preview,
                "message": "Nothing has been created yet. Ask the user to confirm, then call again with confirmed=True."}
    action_id = log_action("create_escalation", account_id, json.dumps(preview), caller_role,
                            order_id=order_id, ticket_id=ticket_id)
    return {"status": "CREATED", "escalation_id": action_id, **preview}


@mcp.tool()
def update_ticket_status(ticket_id: str, account_id: str, caller_role: str, new_status: str,
                          note: str = "", confirmed: bool = False) -> dict:
    """Update a ticket's status (e.g. to 'escalated', 'pending_customer',
    'resolved'). Preview-then-confirm, same contract as create_escalation."""
    if caller_role != "staff":
        return {"error": "access_denied", "detail": "Only staff may update ticket status."}
    preview = {"action": "update_ticket_status", "ticket_id": ticket_id, "account_id": account_id,
               "new_status": new_status, "note": note}
    if not confirmed:
        return {"status": "PREVIEW_ONLY", "would_update": preview,
                "message": "Nothing has been updated yet. Ask the user to confirm, then call again with confirmed=True."}
    action_id = log_action("update_ticket_status", account_id, json.dumps(preview), caller_role, ticket_id=ticket_id)
    return {"status": "UPDATED", "action_id": action_id, **preview}


@mcp.tool()
def create_followup_task(account_id: str, caller_role: str, description: str, assignee: str = "unassigned",
                          order_id: str = "", ticket_id: str = "", confirmed: bool = False) -> dict:
    """Create an internal follow-up task (e.g. 'verify carrier fault with
    SwiftShip before issuing credit'). Preview-then-confirm, same contract."""
    if caller_role != "staff":
        return {"error": "access_denied", "detail": "Only staff may create follow-up tasks."}
    preview = {"action": "create_followup_task", "account_id": account_id, "order_id": order_id,
               "ticket_id": ticket_id, "assignee": assignee, "description": description}
    if not confirmed:
        return {"status": "PREVIEW_ONLY", "would_create": preview,
                "message": "Nothing has been created yet. Ask the user to confirm, then call again with confirmed=True."}
    action_id = log_action("create_followup_task", account_id, json.dumps(preview), caller_role,
                            order_id=order_id, ticket_id=ticket_id)
    return {"status": "CREATED", "task_id": action_id, **preview}


@mcp.tool()
def list_recent_actions(caller_role: str, limit: int = 20) -> list[dict]:
    """Staff-only: list recently logged actions (escalations, ticket updates, tasks)."""
    if caller_role != "staff":
        return [{"error": "access_denied"}]
    return list_actions()[:limit]


if __name__ == "__main__":
    mcp.run(transport="stdio")
