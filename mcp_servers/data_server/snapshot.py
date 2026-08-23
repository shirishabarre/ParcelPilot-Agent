"""
The task spec requires all time-based questions to use the dataset snapshot
time from the workbook's README sheet, not wall-clock 'now'. This module
reads and caches that value.
"""
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
XLSX_PATH = ROOT / "data" / "raw" / "ParcelPilot_Assessment_Data.xlsx"


def get_snapshot_time() -> datetime:
    readme = pd.read_excel(XLSX_PATH, sheet_name="README", header=None)
    row = readme[readme[0] == "Dataset snapshot"]
    if row.empty:
        raise ValueError("Dataset snapshot row not found in README sheet")
    raw = row.iloc[0, 1]
    # value looks like '2026-08-16 11:00 Asia/Kolkata' -> strip tz label, treat as naive local time
    text = str(raw).replace("Asia/Kolkata", "").strip()
    return datetime.fromisoformat(text)
