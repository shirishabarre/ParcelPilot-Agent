"""
Deterministic business-rule calculators for cancellation fees and
failed-pickup service credits. Applies source precedence: a signed
customer agreement overrides the default SOP field-by-field.
"""
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
TERMS_PATH = ROOT / "data" / "contract_terms.yaml"


def _load_terms() -> dict:
    with open(TERMS_PATH) as f:
        return yaml.safe_load(f)


def _parse(dt):
    if dt is None or (isinstance(dt, float)):
        return None
    if isinstance(dt, datetime):
        return dt
    return datetime.fromisoformat(str(dt))


def calculate_cancellation_fee(order: dict, account_id: str) -> dict:
    """
    order: dict with keys status, booked_at, cancellation_requested_at
    Returns a decision with the fee, whether cancellation is even allowed,
    and the source doc(s) that justify it.
    """
    terms = _load_terms()
    default = terms["default_sop"]
    override = terms["account_overrides"].get(account_id, {})
    sources = [default["source_doc"]]

    status = order.get("status")

    if status == "DELIVERED":
        return {"cancellable": False, "fee_inr": None,
                "reason": "DELIVERED shipments cannot be cancelled.",
                "sources": sources}

    if status == "PICKED_UP":
        return {"cancellable": False, "fee_inr": None,
                "reason": "PICKED_UP shipments cannot be cancelled; use the return-to-origin workflow instead.",
                "sources": sources}

    if status == "DRAFT":
        return {"cancellable": True, "fee_inr": 0,
                "reason": "DRAFT orders may be cancelled with no fee.",
                "sources": sources}

    if status == "BOOKED":
        cxl_override = override.get("cancellation", {})
        if cxl_override.get("waive_fee_if_not_picked_up"):
            sources.append(override["source_doc"])
            return {"cancellable": True, "fee_inr": 0,
                    "reason": ("Signed agreement waives the cancellation fee for any BOOKED, "
                               "not-yet-picked-up shipment regardless of time since booking."),
                    "sources": sources}

        booked_at = _parse(order.get("booked_at"))
        requested_at = _parse(order.get("cancellation_requested_at"))
        if not booked_at or not requested_at:
            return {"cancellable": None, "fee_inr": None,
                    "reason": "Missing booked_at or cancellation_requested_at — cannot determine fee. Verify before acting.",
                    "sources": sources, "needs_verification": True}

        minutes_since_booking = (requested_at - booked_at).total_seconds() / 60
        grace = default["cancellation"]["booked_grace_minutes"]
        fee = default["cancellation"]["booked_fee_inr"]

        if minutes_since_booking <= grace:
            return {"cancellable": True, "fee_inr": 0,
                    "reason": f"Cancellation requested {minutes_since_booking:.0f} min after booking, within the {grace}-min no-fee grace window.",
                    "sources": sources}
        else:
            return {"cancellable": True, "fee_inr": fee,
                    "reason": f"Cancellation requested {minutes_since_booking:.0f} min after booking, past the {grace}-min grace window -> INR {fee} fee applies.",
                    "sources": sources}

    return {"cancellable": None, "fee_inr": None,
            "reason": f"Unrecognised order status '{status}'.", "sources": sources,
            "needs_verification": True}


def calculate_service_credit(order: dict, account_id: str) -> dict:
    """
    order: dict with keys pickup_window_end, pickup_actual_at, carrier_fault,
           customer_fault, shipment_fee_inr, status
    """
    terms = _load_terms()
    default = terms["default_sop"]
    override = terms["account_overrides"].get(account_id, {})
    sc_override = override.get("service_credit", {})
    sources = [default["source_doc"]]
    if sc_override:
        sources.append(override["source_doc"])

    carrier_fault = order.get("carrier_fault")
    customer_fault = order.get("customer_fault")

    if carrier_fault is None or customer_fault is None:
        return {"eligible": None, "credit_inr": None,
                "reason": "carrier_fault/customer_fault unknown — do not promise a credit until fault is confirmed.",
                "sources": sources, "needs_verification": True}

    if customer_fault:
        return {"eligible": False, "credit_inr": 0,
                "reason": "Customer-caused delay is not eligible for a service credit.",
                "sources": sources}

    if not carrier_fault:
        return {"eligible": False, "credit_inr": 0,
                "reason": "No carrier fault recorded — not eligible under the default policy.",
                "sources": sources}

    window_end = _parse(order.get("pickup_window_end"))
    pickup_actual = _parse(order.get("pickup_actual_at"))
    reference_time = pickup_actual  # if not yet picked up, caller should pass current snapshot time as pickup_actual for an "as of now" check

    if window_end is None or reference_time is None:
        return {"eligible": None, "credit_inr": None,
                "reason": "Missing pickup_window_end or a reference time to compare against — cannot determine delay.",
                "sources": sources, "needs_verification": True}

    delay_hours = (reference_time - window_end).total_seconds() / 3600
    threshold = sc_override.get("delay_threshold_hours", default["service_credit"]["delay_threshold_hours"])

    if delay_hours <= threshold:
        return {"eligible": False, "credit_inr": 0,
                "reason": f"Delay is {delay_hours:.1f}h, at/under the {threshold}h threshold required for a credit.",
                "sources": sources}

    if "fixed_credit_inr" in sc_override:
        credit = sc_override["fixed_credit_inr"]
        reason = (f"Delay is {delay_hours:.1f}h, past the contract-specific {threshold}h threshold -> "
                  f"fixed INR {credit} credit per signed agreement (replaces default formula).")
    else:
        cap = sc_override.get("credit_cap_inr", default["service_credit"]["credit_cap_inr"])
        pct = sc_override.get("credit_percent_of_fee", default["service_credit"]["credit_percent_of_fee"])
        fee = order.get("shipment_fee_inr") or 0
        credit = round(min(cap, pct * fee), 2)
        reason = (f"Delay is {delay_hours:.1f}h, past the {threshold}h threshold -> "
                  f"credit = min(INR {cap}, {int(pct*100)}% of INR {fee} fee) = INR {credit}.")

    approval_threshold = default["service_credit"]["manager_approval_above_inr"]
    needs_approval = credit > approval_threshold

    result = {"eligible": True, "credit_inr": credit, "reason": reason, "sources": sources,
              "needs_manager_approval": needs_approval}

    monthly_cap = sc_override.get("monthly_aggregate_cap_inr")
    if monthly_cap:
        result["note"] = (f"Account has a monthly aggregate service-credit cap of INR {monthly_cap} — "
                           f"verify month-to-date credits issued before finalising.")
    return result
