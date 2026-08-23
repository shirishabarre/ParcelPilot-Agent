"""
Quick sanity check to run after cloning / before deploying: confirms the
xlsx has the expected sheets/columns and that the snapshot time parses.
Run: python scripts/seed_check.py
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mcp_servers" / "data_server"))
from snapshot import get_snapshot_time  # noqa: E402

XLSX_PATH = ROOT / "data" / "raw" / "ParcelPilot_Assessment_Data.xlsx"

EXPECTED = {
    "accounts": {"account_id", "account_name", "plan", "status", "csm", "contract_file"},
    "orders": {"order_id", "account_id", "status"},
    "tickets": {"ticket_id", "account_id", "status", "subject", "description"},
}


def main():
    ok = True
    if not XLSX_PATH.exists():
        print(f"MISSING: {XLSX_PATH}")
        sys.exit(1)

    for sheet, required_cols in EXPECTED.items():
        df = pd.read_excel(XLSX_PATH, sheet_name=sheet)
        missing = required_cols - set(df.columns)
        if missing:
            print(f"FAIL: sheet '{sheet}' missing columns: {missing}")
            ok = False
        else:
            print(f"OK: sheet '{sheet}' has {len(df)} rows, required columns present")

    try:
        snap = get_snapshot_time()
        print(f"OK: dataset snapshot time = {snap}")
    except Exception as e:
        print(f"FAIL: could not parse snapshot time: {e}")
        ok = False

    required_pdfs = [
        "01_Support_Policy_v3_CURRENT.pdf", "02_Support_Policy_v2_DEPRECATED.pdf",
        "03_Cancellation_and_Service_Credit_SOP_v4.pdf", "04_Product_Operations_Guide_and_Known_Issues.pdf",
        "05_Northstar_Logistics_Enterprise_Agreement.pdf", "06_LumenWorks_Service_Agreement.pdf",
    ]
    for pdf in required_pdfs:
        if not (ROOT / "data" / "raw" / pdf).exists():
            print(f"FAIL: missing {pdf}")
            ok = False

    if not ok:
        sys.exit(1)
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
