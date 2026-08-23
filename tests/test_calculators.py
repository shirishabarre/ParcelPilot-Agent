import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp_servers" / "data_server"))
from calculators import calculate_cancellation_fee, calculate_service_credit  # noqa: E402


def test_northstar_cancellation_always_waived():
    order = {"status": "BOOKED", "booked_at": "2026-08-16T09:00:00", "cancellation_requested_at": "2026-08-16T12:00:00"}
    r = calculate_cancellation_fee(order, "ACCT-001")
    assert r["cancellable"] is True
    assert r["fee_inr"] == 0
    assert "05_Northstar_Logistics_Enterprise_Agreement.pdf" in r["sources"]


def test_default_sop_grace_window_no_fee():
    order = {"status": "BOOKED", "booked_at": "2026-08-16T09:00:00", "cancellation_requested_at": "2026-08-16T09:15:00"}
    r = calculate_cancellation_fee(order, "ACCT-003")  # Beacon, no contract override
    assert r["fee_inr"] == 0


def test_default_sop_fee_after_grace():
    order = {"status": "BOOKED", "booked_at": "2026-08-16T08:00:00", "cancellation_requested_at": "2026-08-16T09:15:00"}
    r = calculate_cancellation_fee(order, "ACCT-002")  # LumenWorks, no cancellation override
    assert r["fee_inr"] == 250


def test_picked_up_cannot_cancel():
    order = {"status": "PICKED_UP"}
    r = calculate_cancellation_fee(order, "ACCT-001")
    assert r["cancellable"] is False


def test_delivered_cannot_cancel():
    order = {"status": "DELIVERED"}
    r = calculate_cancellation_fee(order, "ACCT-002")
    assert r["cancellable"] is False


def test_lumenworks_fixed_credit_replaces_default_formula():
    order = {
        "carrier_fault": True, "customer_fault": False,
        "pickup_window_end": "2026-08-16T08:00:00", "pickup_actual_at": "2026-08-16T12:30:00",  # 4.5h late
        "shipment_fee_inr": 2000,
    }
    r = calculate_service_credit(order, "ACCT-002")
    assert r["eligible"] is True
    assert r["credit_inr"] == 300  # fixed, not min(500, 10%*2000)=200


def test_lumenworks_under_threshold_not_eligible():
    order = {
        "carrier_fault": True, "customer_fault": False,
        "pickup_window_end": "2026-08-16T08:00:00", "pickup_actual_at": "2026-08-16T10:30:00",  # 2.5h late, under 4h
        "shipment_fee_inr": 2000,
    }
    r = calculate_service_credit(order, "ACCT-002")
    assert r["eligible"] is False


def test_default_formula_caps_at_500():
    order = {
        "carrier_fault": True, "customer_fault": False,
        "pickup_window_end": "2026-08-16T08:00:00", "pickup_actual_at": "2026-08-16T11:00:00",  # 3h late
        "shipment_fee_inr": 10000,  # 10% would be 1000, capped at 500
    }
    r = calculate_service_credit(order, "ACCT-003")
    assert r["credit_inr"] == 500
    assert r["needs_manager_approval"] is False  # exactly at threshold, not above


def test_missing_fault_data_never_promises_credit():
    order = {"pickup_window_end": "2026-08-16T08:00:00", "pickup_actual_at": "2026-08-16T12:00:00"}
    r = calculate_service_credit(order, "ACCT-003")
    assert r["eligible"] is None
    assert r.get("needs_verification") is True


def test_customer_fault_never_eligible():
    order = {"carrier_fault": True, "customer_fault": True,
             "pickup_window_end": "2026-08-16T08:00:00", "pickup_actual_at": "2026-08-16T12:00:00"}
    r = calculate_service_credit(order, "ACCT-003")
    assert r["eligible"] is False


def test_manager_approval_flag_above_1000():
    order = {
        "carrier_fault": True, "customer_fault": False,
        "pickup_window_end": "2026-08-16T08:00:00", "pickup_actual_at": "2026-08-16T15:00:00",
        "shipment_fee_inr": 100000,  # would be huge without cap; but default cap is 500, so this can't trigger >1000
    }
    r = calculate_service_credit(order, "ACCT-003")
    assert r["credit_inr"] == 500  # capped
    assert r["needs_manager_approval"] is False
