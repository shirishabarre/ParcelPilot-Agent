import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp_servers" / "docs_server"))
from retriever import DocRetriever  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp_servers" / "data_server"))
from calculators import calculate_cancellation_fee  # noqa: E402

retriever = DocRetriever()


def test_deprecated_policy_never_indexed():
    ids = {r["doc_id"] for r in retriever.records}
    assert "02_Support_Policy_v2_DEPRECATED.pdf" not in ids


def test_deprecated_policy_never_returned_for_any_query():
    for q in ["P1 response time", "severity", "escalation", "support policy"]:
        results = retriever.search(q, top_k=10)
        assert all(r["doc_id"] != "02_Support_Policy_v2_DEPRECATED.pdf" for r in results)


def test_customers_contract_not_visible_to_other_customer():
    # LumenWorks (ACCT-002) should never see Northstar's contract in a scoped search
    results = retriever.search("cancellation fee waiver", account_scope="ACCT-002", top_k=10)
    assert all(r["doc_id"] != "05_Northstar_Logistics_Enterprise_Agreement.pdf" for r in results)


def test_contract_overrides_default_sop_for_northstar():
    # This mirrors TKT-450's WRONG historical resolution: agent told customer a INR 250 fee
    # applied after 30 minutes. The correct answer (per the signed contract) is INR 0, always.
    order = {"status": "BOOKED", "booked_at": "2026-08-16T09:00:00", "cancellation_requested_at": "2026-08-16T10:30:00"}  # 90 min later
    result = calculate_cancellation_fee(order, "ACCT-001")
    assert result["fee_inr"] == 0, "Contract waiver must override the default 250 INR fee, contradicting the wrong historical ticket resolution"


def test_growth_plan_bulk_upload_limit_is_5000_not_3000():
    # This mirrors TKT-451's WRONG historical resolution: agent told customer "Growth plan only
    # supports 3,000 rows." The current product doc says the supported limit is 5,000 rows;
    # ~3,000 is only where KI-208's *intermittent bug* starts appearing, not the product limit.
    results = retriever.search("bulk upload supported row limit Growth", top_k=5)
    assert any(r["doc_id"] == "04_Product_Operations_Guide_and_Known_Issues.pdf" for r in results)
    # (Numeric assertion on "5000" is left to the LLM-facing answer; this test guards that the
    #  CURRENT product doc — not a historical ticket — is what gets retrieved for this question.)
