# Architecture

## Overview

```
                 ┌─────────────────────────────────────────┐
                 │            Streamlit Frontend             │
                 │  (Customer Chat | Internal Chat | Dash)   │
                 └───────────────────┬───────────────────────┘
                                     │ session (role, account_id) — mock auth
                                     ▼
                 ┌─────────────────────────────────────────┐
                 │         agent_core/orchestrator.py         │
                 │   MCP CLIENT + tool-use loop (Gemini/Groq) │
                 │  - injects real caller_role/account_id     │
                 │  - forces confirmed=False on model calls   │
                 │  - conflict_detector for uncertainty        │
                 └──────┬───────────────┬───────────────┬────┘
                        │ MCP/stdio      │ MCP/stdio     │ MCP/stdio
                        ▼                ▼               ▼
              ┌─────────────┐   ┌──────────────┐  ┌───────────────┐
              │ docs_server  │   │ data_server   │  │ actions_server │
              │ (Tool 1)     │   │ (Tool 2)      │  │ (Tool 3)       │
              │ BM25 search  │   │ pandas over   │  │ SQLite mock,   │
              │ over chunked │   │ xlsx, account-│  │ confirm-gated  │
              │ + tagged PDFs│   │ scoped        │  │                │
              └─────┬────────┘   └──────┬────────┘  └───────┬────────┘
                    │                   │                    │
                    ▼                   ▼                    ▼
         data/processed/       data/raw/*.xlsx        actions_log.db
         chunks.jsonl          data/contract_terms.yaml
         (from data/raw/*.pdf)
```

## Why MCP servers as the 3 tools

Each of the three required tool categories is its own MCP server (own
process, own tool schema, own access-control checks), rather than three
Python functions bundled into one server. This means:
- Access control is enforced per-server at the boundary the orchestrator
  actually calls through — a bug in the docs server's logic can't leak into
  the data server's account scoping.
- Any of the three servers could be swapped for a real service later
  (e.g. actions_server → a real Zendesk/Jira MCP connector) without
  touching the other two or the orchestrator's tool-dispatch logic.
- The same servers can be pointed to from Claude Desktop or any other MCP
  client via `mcp_servers.json`, not just this app.

## Why this LLM/embedding setup is free

- **LLM**: Gemini's AI Studio free tier (or Groq's free tier) — both have
  no-cost quotas sufficient for a demo/assessment volume of traffic.
- **Embeddings/retrieval**: BM25 (rank_bm25, pure Python, runs locally) with
  an authority-weight rerank, instead of a hosted embedding API. This is a
  deliberate trade-off: BM25 is weaker than semantic embeddings for
  paraphrased queries, but the source pack is small (6 documents) and the
  vocabulary is domain-specific/policy language where keyword match works
  well — and it costs nothing and requires no network call.
- **Vector/DB**: none needed — `chunks.jsonl` + in-memory BM25 index.
- **Actions**: SQLite file, not a hosted queue/ticketing service.

## Data flow for a typical multi-step question

"Can Northstar cancel ORD-1001 without a fee?"

1. Orchestrator calls `data_server.get_order("ORD-1001", ...)` → gets
   `account_id=ACCT-001`, `status=BOOKED`.
2. Calls `docs_server.search_documents("cancellation fee waiver", account_scope="ACCT-001")`
   → surfaces the Northstar contract clause (ranked above the general SOP
   because of the authority-weighted rerank).
3. Calls `data_server.calculate_cancellation` → rule engine checks the
   Northstar override in `contract_terms.yaml` first → returns fee=0 with
   the specific source doc(s) that justify it.
4. Orchestrator/LLM composes the final answer, citing the contract.
5. No action tool is needed here since nothing changes state — if the user
   then says "escalate this to check with the CSM," the orchestrator calls
   `actions_server.create_escalation(..., confirmed=False)` for a preview
   first.

## Access control enforcement points (not just prompting)

| Layer | Enforcement |
|---|---|
| `mcp_servers/data_server/repository.py` | `_check_scope()` raises `AccessDeniedError` if a customer's `caller_account_id` doesn't match the requested `account_id` — runs on every read. |
| `mcp_servers/docs_server/retriever.py` | `account_scope` filters out any chunk whose `account_scope` isn't `"all"` or the caller's own account — a customer's search can never surface another customer's contract. |
| `agent_core/orchestrator.py` | `_inject_scope()` overwrites `caller_role`/`caller_account_id` in every tool call with the authenticated session's real values, discarding whatever the model put there. |
| `mcp_servers/actions_server/server.py` | `update_ticket_status` / `create_followup_task` reject any `caller_role != "staff"`; every action tool ignores a model-supplied `confirmed=True` (overwritten to `False` by the orchestrator) until the human clicks Confirm. |

## Confirm-before-action flow

1. Model calls e.g. `create_escalation(..., confirmed=False)` (orchestrator
   forces this regardless of what the model passed).
2. Tool returns `{"status": "PREVIEW_ONLY", "would_create": {...}}`.
3. Orchestrator surfaces this as `pending_action` in `TurnResult`.
4. Streamlit renders the preview + Confirm/Cancel buttons
   (`frontend/components/confirm_modal.py`).
5. Only a literal button click calls `orchestrator.execute_confirmed_action()`,
   which re-invokes the *exact same* tool/arguments captured in the preview
   with `confirmed=True` — the model is never given a path to self-confirm.
