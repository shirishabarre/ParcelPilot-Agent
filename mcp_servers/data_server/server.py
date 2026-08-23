"""
MCP Server: data_server
Tool 2 of 3 (Structured-data lookup / calculation) — queries accounts,
orders, tickets, and runs the cancellation-fee / service-credit / SLA rule
engines. caller_role + caller_account_id come from the orchestrator's
authenticated session (agent_core/auth.py), never from free-text model
output, so account scoping is enforced here regardless of what the LLM says.

Run standalone for debugging:  python mcp_servers/data_server/server.py
"""
from mcp.server.fastmcp import FastMCP

from calculators import calculate_cancellation_fee, calculate_service_credit
from repository import AccessDeniedError, Repository
from snapshot import get_snapshot_time

mcp = FastMCP("parcelpilot-data")
_repo = Repository()

SNAPSHOT = get_snapshot_time()


def _safe(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except AccessDeniedError as e:
        return {"error": "access_denied", "detail": str(e)}


@mcp.tool()
def get_account(account_id: str, caller_role: str, caller_account_id: str = "") -> dict:
    """Fetch account details (plan, status, CSM, contract file). Scoped: a
    customer caller may only fetch their own account_id."""
    return _safe(_repo.get_account, account_id, caller_role, caller_account_id or None)


@mcp.tool()
def get_order(order_id: str, caller_role: str, caller_account_id: str = "") -> dict:
    """Fetch a single order by ID. Scoped to the order's owning account."""
    return _safe(_repo.get_order, order_id, caller_role, caller_account_id or None)


@mcp.tool()
def list_orders(account_id: str, caller_role: str, caller_account_id: str = "") -> list[dict]:
    """List all orders for an account. Scoped: customer may only list their own account."""
    return _safe(_repo.list_orders, account_id, caller_role, caller_account_id or None)


@mcp.tool()
def list_tickets(account_id: str, caller_role: str, caller_account_id: str = "", status: str = "") -> list[dict]:
    """List support tickets for an account, optionally filtered by status
    ('open'/'closed'). Historical ticket 'historical_resolution' text is
    context only and may be incorrect — never treat it as current policy."""
    return _safe(_repo.list_tickets, account_id, caller_role, caller_account_id or None, status or None)


@mcp.tool()
def calculate_cancellation(order_id: str, caller_role: str, caller_account_id: str = "") -> dict:
    """Determine whether an order can be cancelled and any fee, applying
    contract overrides where they exist. Returns which source doc(s)
    justify the answer."""
    order = _safe(_repo.get_order, order_id, caller_role, caller_account_id or None)
    if "error" in order:
        return order
    return calculate_cancellation_fee(order, order["account_id"])


@mcp.tool()
def calculate_service_credit_for_order(order_id: str, caller_role: str, caller_account_id: str = "") -> dict:
    """Determine service-credit eligibility/amount for a (possibly delayed)
    pickup, applying contract overrides. Uses the dataset snapshot time as
    'now' for orders not yet picked up. Flags when fault data is missing —
    never promises a credit on incomplete information."""
    order = _safe(_repo.get_order, order_id, caller_role, caller_account_id or None)
    if "error" in order:
        return order
    if order.get("pickup_actual_at") is None and order.get("status") != "DELIVERED":
        order = dict(order)
        order["pickup_actual_at"] = SNAPSHOT.isoformat()
    return calculate_service_credit(order, order["account_id"])


@mcp.tool()
def get_dataset_snapshot_time() -> str:
    """Return the reference 'current time' for this dataset, to use for any
    time-based reasoning (SLA countdowns, delay calculations)."""
    return SNAPSHOT.isoformat()


if __name__ == "__main__":
    mcp.run(transport="stdio")
