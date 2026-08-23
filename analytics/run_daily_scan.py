"""
Entry point for the proactive-issue digest shown on the internal dashboard.
Run on a schedule (cron/Task Scheduler) in production; here it's callable
directly by the Streamlit dashboard page or via `python run_daily_scan.py`.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from anomaly_detector import correlate_known_issues, volume_anomalies
from cluster_issues import cluster_tickets
from sla_monitor import scan as scan_sla

OUT_PATH = Path(__file__).resolve().parent / "output" / "issues_digest.json"


def run_scan() -> dict:
    digest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sla_risk": scan_sla(),
        "recurring_issue_clusters": cluster_tickets(),
        "known_issue_correlation": correlate_known_issues(),
        "volume_anomalies": volume_anomalies(),
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(digest, f, indent=2, default=str)
    return digest


if __name__ == "__main__":
    d = run_scan()
    print(f"SLA risk items: {len(d['sla_risk'])}")
    print(f"Recurring clusters: {len(d['recurring_issue_clusters'])}")
    print(f"Known-issue matches: {len(d['known_issue_correlation'])}")
    print(f"Volume anomalies: {len(d['volume_anomalies'])}")
    print(f"Digest written to {OUT_PATH}")
