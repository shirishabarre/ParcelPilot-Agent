"""
Flags open tickets approaching or exceeding their first-response SLA
target, using contract overrides (Northstar/LumenWorks) where they exist
and the default Support Policy v3 plan table otherwise. Severity isn't a
field in the ticket data, so it's inferred with simple keyword heuristics —
in production this would be a real field set at intake; this is a
transparent stand-in, and every flagged ticket shows WHY it got its
severity/target so a human can override it.
"""
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mcp_servers" / "data_server"))
from snapshot import get_snapshot_time  # noqa: E402

XLSX_PATH = ROOT / "data" / "raw" / "ParcelPilot_Assessment_Data.xlsx"

# Default plan targets (minutes) from 01_Support_Policy_v3_CURRENT.pdf
DEFAULT_TARGETS_MIN = {
    "Enterprise": {"P1": 30, "P2": 120, "P3": 480},     # 30m / 2h / 1 business day (approx 8h)
    "Growth":     {"P1": 120, "P2": 240, "P3": 960},    # 2 biz hr / 4 biz hr / 2 biz days (approx)
    "Standard":   {"P1": 240, "P2": 480, "P3": 960},
}

# Contract overrides (minutes) from signed agreements — see data/contract_terms.yaml for cancellation/credit;
# support-target overrides are text-only in the PDFs, encoded here for the same reason as contract_terms.yaml.
CONTRACT_TARGET_OVERRIDES_MIN = {
    "ACCT-001": {"P1": 15, "P2": 60, "P3": 480},   # Northstar: 15m / 1h / 8 biz hr
    "ACCT-002": {"P1": 120, "P2": 240, "P3": 960},  # LumenWorks: 2 biz hr / 4 biz hr / 2 biz days
}

P1_KEYWORDS = ["outage", "all shipment", "cannot create", "security", "api key", "exposure", "credential"]
P2_KEYWORDS = ["bulk upload", "fails", "failing", "still shows booked", "degraded", "webhook"]


def infer_severity(subject: str, description: str) -> str:
    text = f"{subject} {description}".lower()
    if any(k in text for k in P1_KEYWORDS):
        return "P1"
    if any(k in text for k in P2_KEYWORDS):
        return "P2"
    return "P3"


def get_target_minutes(account_id: str, plan: str, severity: str) -> int:
    override = CONTRACT_TARGET_OVERRIDES_MIN.get(account_id)
    if override:
        return override[severity]
    return DEFAULT_TARGETS_MIN.get(plan, DEFAULT_TARGETS_MIN["Standard"])[severity]


def scan() -> list[dict]:
    tickets = pd.read_excel(XLSX_PATH, sheet_name="tickets")
    accounts = pd.read_excel(XLSX_PATH, sheet_name="accounts").set_index("account_id")
    now = get_snapshot_time()

    open_tickets = tickets[tickets.status == "open"]
    results = []
    for _, t in open_tickets.iterrows():
        acct = accounts.loc[t.account_id]
        severity = infer_severity(t.subject, t.description)
        target_min = get_target_minutes(t.account_id, acct["plan"], severity)
        created_at = datetime.fromisoformat(str(t.created_at))
        elapsed_min = (now - created_at).total_seconds() / 60
        pct_of_target = elapsed_min / target_min if target_min else 0

        if pct_of_target >= 1.0:
            risk = "BREACHED"
        elif pct_of_target >= 0.8:
            risk = "APPROACHING"
        else:
            risk = "OK"

        results.append({
            "ticket_id": t.ticket_id, "account_id": t.account_id, "account_name": acct["account_name"],
            "plan": acct["plan"], "subject": t.subject, "inferred_severity": severity,
            "target_minutes": target_min, "elapsed_minutes": round(elapsed_min, 1),
            "pct_of_target": round(pct_of_target, 2), "risk": risk,
            "assigned_to": t.assigned_to,
        })

    results.sort(key=lambda r: r["pct_of_target"], reverse=True)
    return results


if __name__ == "__main__":
    for r in scan():
        print(r)
