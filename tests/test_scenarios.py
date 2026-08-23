"""
End-to-end scenario checks against the tool layer directly (data_server +
docs_server + actions_server functions), independent of which LLM provider
is configured. These are the scenarios most worth walking through in the
demo video. Run: python tests/test_scenarios.py  (or via pytest)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp_servers" / "data_server"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp_servers" / "docs_server"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp_servers" / "actions_server"))

from calculators import calculate_cancellation_fee, calculate_service_credit  # noqa: E402
from repository import Repository  # noqa: E402
from retriever import DocRetriever  # noqa: E402
from snapshot import get_snapshot_time  # noqa: E402
from server import create_escalation  # actions_server  # noqa: E402

repo = Repository()
retriever = DocRetriever()
SNAPSHOT = get_snapshot_time()


def _with_snapshot_pickup(order: dict) -> dict:
    """Same rule the data_server MCP tool applies: if not yet picked up, use
    the dataset snapshot time as 'now' for an as-of-now delay check."""
    if order.get("pickup_actual_at") is None and order.get("status") != "DELIVERED":
        order = dict(order)
        order["pickup_actual_at"] = SNAPSHOT.isoformat()
    return order


def scenario_northstar_cancel_ord1001():
    """'Can Northstar cancel ORD-1001 without a cancellation fee? Explain why.'"""
    order = repo.get_order("ORD-1001", caller_role="staff", caller_account_id=None)
    docs = retriever.search("cancellation fee waiver BOOKED shipment", account_scope="ACCT-001", top_k=3)
    result = calculate_cancellation_fee(order, "ACCT-001")
    assert result["fee_inr"] == 0
    assert result["cancellable"] is True
    assert any(d["doc_id"] == "05_Northstar_Logistics_Enterprise_Agreement.pdf" for d in docs)
    print("PASS: ORD-1001 Northstar cancellation ->", result["reason"])


def scenario_lumenworks_delay_credit_ord2002():
    """'A pickup is late because of carrier fault. Should I get a service credit?' (ORD-2002, LumenWorks)"""
    order = _with_snapshot_pickup(repo.get_order("ORD-2002", caller_role="staff", caller_account_id=None))
    result = calculate_service_credit(order, "ACCT-002")
    assert result["eligible"] is True
    assert result["credit_inr"] == 300
    print("PASS: ORD-2002 LumenWorks credit ->", result["reason"])


def scenario_northstar_security_incident_escalation():
    """TKT-505-style: a P1 security incident should be escalatable, preview-then-confirm."""
    preview = create_escalation(account_id="ACCT-004", caller_role="staff", reason="Possible production API key exposure",
                                 severity="P1", ticket_id="TKT-505", confirmed=False)
    assert preview["status"] == "PREVIEW_ONLY"
    confirmed = create_escalation(account_id="ACCT-004", caller_role="staff", reason="Possible production API key exposure",
                                   severity="P1", ticket_id="TKT-505", confirmed=True)
    assert confirmed["status"] == "CREATED"
    print("PASS: TKT-505 escalation preview -> confirm flow, id:", confirmed["escalation_id"])


def scenario_historical_ticket_wrong_guidance_not_trusted():
    """TKT-450's historical_resolution said a 250 INR fee applied after 30 min for Northstar — WRONG,
    the signed contract waives it entirely. The calculator (backed by the contract) must contradict it."""
    order = {"status": "BOOKED", "booked_at": "2026-08-16T09:00:00", "cancellation_requested_at": "2026-08-16T10:30:00"}
    result = calculate_cancellation_fee(order, "ACCT-001")
    assert result["fee_inr"] == 0
    print("PASS: correctly overrides TKT-450's wrong historical guidance ->", result["reason"])


def scenario_customer_cannot_see_other_account_order():
    """A LumenWorks customer session must not be able to fetch a Northstar order."""
    try:
        repo.get_order("ORD-1001", caller_role="customer", caller_account_id="ACCT-002")
        raise AssertionError("Expected AccessDeniedError")
    except Exception as e:
        assert "AccessDenied" in type(e).__name__
        print("PASS: cross-account order access correctly denied ->", e)


if __name__ == "__main__":
    scenario_northstar_cancel_ord1001()
    scenario_lumenworks_delay_credit_ord2002()
    scenario_northstar_security_incident_escalation()
    scenario_historical_ticket_wrong_guidance_not_trusted()
    scenario_customer_cannot_see_other_account_order()
    print("\nAll scenarios passed.")
