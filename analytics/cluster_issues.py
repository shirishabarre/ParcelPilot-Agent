"""
Groups tickets that describe the same underlying issue, so a spike of
individually-filed tickets ("bulk upload fails" reported separately by two
customers) surfaces as one recurring issue rather than N unrelated ones.
Free/local: keyword-overlap (Jaccard on normalized tokens) — no clustering
API/service needed, deliberately simple and auditable.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mcp_servers" / "docs_server"))
from retriever import _tokenize  # noqa: E402

XLSX_PATH = ROOT / "data" / "raw" / "ParcelPilot_Assessment_Data.xlsx"

STOPWORDS = {"the", "a", "an", "to", "for", "is", "are", "of", "on", "in", "still", "we", "do",
             "how", "after", "shows", "row", "rows"}


def _keyset(subject: str, description: str) -> set:
    tokens = _tokenize(f"{subject} {description}")
    return {t for t in tokens if t not in STOPWORDS and len(t) > 2}


def cluster_tickets(jaccard_threshold: float = 0.15) -> list[dict]:
    tickets = pd.read_excel(XLSX_PATH, sheet_name="tickets")
    items = []
    for _, t in tickets.iterrows():
        items.append({
            "ticket_id": t.ticket_id, "account_id": t.account_id, "status": t.status,
            "subject": t.subject, "keys": _keyset(t.subject, t.description),
        })

    visited = set()
    clusters = []
    for i, a in enumerate(items):
        if a["ticket_id"] in visited:
            continue
        group = [a]
        visited.add(a["ticket_id"])
        for b in items[i + 1:]:
            if b["ticket_id"] in visited:
                continue
            inter = a["keys"] & b["keys"]
            union = a["keys"] | b["keys"]
            score = len(inter) / len(union) if union else 0
            if score >= jaccard_threshold:
                group.append(b)
                visited.add(b["ticket_id"])
        if len(group) > 1:
            accounts_involved = sorted({g["account_id"] for g in group})
            clusters.append({
                "cluster_subject_sample": group[0]["subject"],
                "ticket_ids": [g["ticket_id"] for g in group],
                "accounts_involved": accounts_involved,
                "multi_customer": len(accounts_involved) > 1,
                "count": len(group),
            })
    clusters.sort(key=lambda c: (c["multi_customer"], c["count"]), reverse=True)
    return clusters


if __name__ == "__main__":
    for c in cluster_tickets():
        print(c)
