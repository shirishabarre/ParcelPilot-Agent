"""
Extracts text from the source PDFs, splits into chunks, and tags each chunk
with authority metadata from data/source_authority.yaml so the retriever can
rank/filter by reliability instead of treating every source as equal.

Run:  python mcp_servers/docs_server/ingest.py
Output: data/processed/chunks.jsonl
"""
import json
import re
from pathlib import Path

import yaml
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
OUT_PATH = ROOT / "data" / "processed" / "chunks.jsonl"
AUTHORITY_PATH = ROOT / "data" / "source_authority.yaml"

CHUNK_SIZE = 700       # chars per chunk
CHUNK_OVERLAP = 120


def load_authority() -> dict:
    with open(AUTHORITY_PATH) as f:
        return yaml.safe_load(f)


def extract_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    # split on paragraph/section boundaries first, then hard-wrap long ones
    paras = [p.strip() for p in re.split(r"\n\s*\n|\n(?=\d\.\s)|\n(?=[A-Z][a-z]+ \d)", text) if p.strip()]
    chunks = []
    buf = ""
    for p in paras:
        if len(buf) + len(p) + 1 <= size:
            buf = f"{buf}\n{p}".strip()
        else:
            if buf:
                chunks.append(buf)
            if len(p) > size:
                for i in range(0, len(p), size - overlap):
                    chunks.append(p[i:i + size])
                buf = ""
            else:
                buf = p
    if buf:
        chunks.append(buf)
    return chunks


def main():
    authority = load_authority()
    doc_meta = authority["documents"]
    excluded = set(authority.get("excluded_from_answers", []))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    n_chunks = 0
    with open(OUT_PATH, "w") as out:
        for filename, meta in doc_meta.items():
            pdf_path = RAW_DIR / filename
            if not pdf_path.exists():
                print(f"WARNING: {filename} not found in {RAW_DIR}, skipping")
                continue
            text = extract_text(pdf_path)
            for idx, chunk in enumerate(chunk_text(text)):
                record = {
                    "chunk_id": f"{filename}::{idx}",
                    "doc_id": filename,
                    "text": chunk,
                    "doc_type": meta["doc_type"],
                    "status": meta["status"],
                    "effective_date": meta["effective_date"],
                    "account_scope": meta["account_scope"],
                    "excluded_from_answers": filename in excluded,
                }
                out.write(json.dumps(record) + "\n")
                n_chunks += 1
    print(f"Wrote {n_chunks} chunks -> {OUT_PATH}")


if __name__ == "__main__":
    main()
