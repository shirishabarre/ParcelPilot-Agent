#!/usr/bin/env bash
# (Re)builds the document search index from the PDFs in data/raw/.
# Run this once after cloning, and again any time a source PDF changes.
set -e
cd "$(dirname "$0")/.."
python3 mcp_servers/docs_server/ingest.py
