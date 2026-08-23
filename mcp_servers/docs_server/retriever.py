"""
Search over the chunked documents. Free/local: BM25 keyword search (no
embedding API key, no vector DB service) with a post-search rerank/boost
based on source authority (source_authority.yaml) so a CURRENT contract or
policy consistently outranks a DEPRECATED or historical source for the same
keyword match, and DEPRECATED docs are excluded outright.
"""
import json
from pathlib import Path

from rank_bm25 import BM25Okapi

ROOT = Path(__file__).resolve().parents[2]
CHUNKS_PATH = ROOT / "data" / "processed" / "chunks.jsonl"

# Higher = more authoritative. Mirrors data/source_authority.yaml precedence.
AUTHORITY_WEIGHT = {
    "signed_customer_agreement": 1.5,
    "current_policy_or_sop": 1.2,
    "current_product_doc": 1.0,
    "historical_ticket": 0.6,
    "deprecated": 0.0,  # excluded, kept at 0 as a belt-and-suspenders guard
}


def _tokenize(text: str):
    return text.lower().replace("/", " ").replace(",", " ").split()


class DocRetriever:
    def __init__(self, chunks_path: Path = CHUNKS_PATH):
        self.records = []
        with open(chunks_path) as f:
            for line in f:
                rec = json.loads(line)
                if rec.get("excluded_from_answers"):
                    continue  # e.g. Support Policy v2 DEPRECATED never enters the index
                self.records.append(rec)
        self._corpus_tokens = [_tokenize(r["text"]) for r in self.records]
        self.bm25 = BM25Okapi(self._corpus_tokens) if self._corpus_tokens else None

    def search(self, query: str, top_k: int = 5, account_scope: str | None = None):
        """
        account_scope: if provided (e.g. 'ACCT-001'), boosts that account's
        specific contract and does not filter out general (account_scope='all')
        documents -> a customer still sees general policy plus their own contract.
        """
        if not self.bm25:
            return []
        scores = self.bm25.get_scores(_tokenize(query))
        ranked = []
        for rec, score in zip(self.records, scores):
            if score <= 0:
                continue
            weight = AUTHORITY_WEIGHT.get(rec["doc_type"], 1.0)
            if account_scope and rec["account_scope"] not in ("all", account_scope):
                continue  # a different customer's contract is never surfaced
            if account_scope and rec["account_scope"] == account_scope:
                weight *= 1.3  # boost this account's own contract further
            ranked.append((score * weight, rec))
        ranked.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, rec in ranked[:top_k]:
            results.append({
                "chunk_id": rec["chunk_id"],
                "doc_id": rec["doc_id"],
                "text": rec["text"],
                "doc_type": rec["doc_type"],
                "status": rec["status"],
                "effective_date": rec["effective_date"],
                "relevance_score": round(float(score), 3),
            })
        return results

    def get_document_chunks(self, doc_id: str):
        return [r for r in self.records if r["doc_id"] == doc_id]
