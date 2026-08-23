"""
Correlates open/recent tickets against 04_Product_Operations_Guide's known
issues (KI-208 bulk-upload failures, KI-211 SwiftShip webhook delay) so the
team sees "this is a known, already-being-worked issue affecting N
customers" instead of independently investigating each ticket from scratch.
Also flags accounts with an unusual ticket volume (>1 open ticket) as a
simple volume-anomaly signal.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
XLSX_PATH = ROOT / "data" / "raw" / "ParcelPilot_Assessment_Data.xlsx"

KNOWN_ISSUES = [
    {
        "id": "KI-208",
        "title": "Bulk Upload failures on large CSVs",
        "status": "Investigating",
        "match_keywords": ["bulk upload", "csv", "large csv", "upload fail"],
        "source_doc": "04_Product_Operations_Guide_and_Known_Issues.pdf",
    },
    {
        "id": "KI-211",
        "title": "SwiftShip pickup webhook delay",
        "status": "Monitoring",
        "match_keywords": ["swiftship", "webhook", "still shows booked", "booked after"],
        "source_doc": "04_Product_Operations_Guide_and_Known_Issues.pdf",
    },
]


def _matches(subject: str, description: str, keywords: list[str]) -> bool:
    text = f"{subject} {description}".lower()
    return any(k in text for k in keywords)


def correlate_known_issues() -> list[dict]:
    tickets = pd.read_excel(XLSX_PATH, sheet_name="tickets")
    findings = []
    for ki in KNOWN_ISSUES:
        matched = tickets[tickets.apply(
            lambda t: _matches(t.subject, t.description, ki["match_keywords"]), axis=1
        )]
        if matched.empty:
            continue
        accounts = sorted(matched.account_id.unique().tolist())
        findings.append({
            "known_issue": ki["id"], "title": ki["title"], "product_status": ki["status"],
            "matched_tickets": matched.ticket_id.tolist(),
            "accounts_involved": accounts,
            "multi_customer": len(accounts) > 1,
            "note": f"Link customer to {ki['id']} (status: {ki['status']}) instead of treating as a new/unrelated bug.",
            "source_doc": ki["source_doc"],
        })
    return findings


def volume_anomalies(min_open_tickets: int = 2) -> list[dict]:
    tickets = pd.read_excel(XLSX_PATH, sheet_name="tickets")
    accounts = pd.read_excel(XLSX_PATH, sheet_name="accounts").set_index("account_id")
    open_tickets = tickets[tickets.status == "open"]
    counts = open_tickets.groupby("account_id").size()
    flagged = counts[counts >= min_open_tickets]
    return [
        {"account_id": acc, "account_name": accounts.loc[acc, "account_name"], "open_ticket_count": int(cnt)}
        for acc, cnt in flagged.items()
    ]


if __name__ == "__main__":
    print("=== Known-issue correlation ===")
    for f in correlate_known_issues():
        print(f)
    print("\n=== Volume anomalies (accounts with multiple open tickets) ===")
    for a in volume_anomalies():
        print(a)
