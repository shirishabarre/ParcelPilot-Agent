# Key Decisions

## 1. Source precedence is data, not model judgment
`data/source_authority.yaml` and `data/contract_terms.yaml` encode the
precedence rules explicitly (signed contract → current policy/SOP → current
product doc → historical ticket, with v2 policy excluded outright). The
retriever and calculators consult these files directly. This means the
system can't "forget" that v2 is deprecated or accidentally weight a wrong
historical ticket resolution as highly as the SOP — it's structurally
impossible for those to outrank the contract/current-policy tier, not just
discouraged by a system prompt.

**Why it matters (validated against the actual data):** ticket TKT-450's
`historical_resolution` field says a customer was told a 250 INR fee applied
after 30 minutes — but Northstar's contract actually waives the fee
entirely, always. TKT-451's resolution says "Growth plan only supports 3,000
rows" — but the current product doc's real limit is 5,000 rows (3,000 is
just where the *bug* KI-208 starts appearing). Both are exactly the kind of
plausible-but-wrong guidance the brief warns about, and both are covered by
`tests/test_source_precedence.py`.

## 2. Access control lives in the tool layer, enforced twice
The task requires enforcement "in the data/tool layer rather than relying
only on model instructions." This is done in two places for defense in
depth: (a) `repository.py`/`retriever.py` reject/filter based on the
`caller_role`/`caller_account_id`/`account_scope` arguments they receive,
and (b) `orchestrator.py` overwrites those arguments with the real
authenticated session before the call ever reaches the tool — so even if
the LLM is convinced to lie about who's asking, the true session wins.

## 3. Numeric contract terms are extracted to YAML; full text stays searchable
Contracts are PDFs (unstructured text). For deterministic math (a fee is
either 0 or 250, not "probably 0"), `calculators.py` reads structured
numbers from `contract_terms.yaml`, extracted once from the signed
agreements. The full contract text remains searchable via `docs_server` so
the agent can still cite/quote the actual clause as justification — the
YAML is for *arithmetic*, the PDF is for *evidence*. This avoids the failure
mode of an LLM doing date/time or percentage math from prose.

## 4. Missing data triggers escalation, not a guess
Both calculators return `needs_verification: true` (never a confident
number) when required fields (carrier fault, timestamps) are absent —
mirroring the SOP's own instruction: "Do not promise a credit when carrier
fault, pickup timing, or customer fault is unknown." The orchestrator's
`conflict_detector.py` treats this as a hard escalate signal.

## 5. Confirm-before-action can't be bypassed by the model
Every action tool takes `confirmed: bool`. The orchestrator hard-codes
`confirmed=False` on any model-initiated call, no matter what the model
passes — a real `confirmed=True` write only happens through
`execute_confirmed_action()`, called exclusively by a UI button click tied
to the exact preview shown to the human. This was a deliberate choice over
"trust the model to ask before setting confirmed=True," since that would
still be model-instruction-only enforcement.

## 6. Streamlit + local subprocess MCP servers, not a hosted backend
Given "free resources" and "simple hosting" goals, running the three MCP
servers as stdio subprocesses spawned by the Streamlit process (rather than
separately hosted services) means one deployable app, zero extra
infrastructure cost, and no network round-trips beyond the LLM call itself.
The trade-off — reconnecting subprocesses each turn — is fine at demo scale;
`docs/ARCHITECTURE.md`'s "what's next" section notes the persistent-session
upgrade path for production.

## 7. BM25 instead of embeddings for document search
Chosen for zero API cost and zero extra infra (no vector DB service), and
because the source pack is small and policy-language-heavy, where exact
terms ("BOOKED", "P1", "cancellation fee") matter more than semantic
paraphrase matching. The authority-weighted rerank compensates for BM25's
weaker semantic matching by making sure that *when* multiple sources match,
the right one wins.

## 8. Severity/SLA-target overrides for support-response targets are also
structured (`analytics/sla_monitor.py`), for the same reason as #3 — SLA
math needs to be exact, not inferred from prose each time.

---

# What I'd build next (prioritized)

1. **Persistent MCP sessions instead of per-turn subprocess spawn.** Biggest
   latency win for production; today each chat turn reconnects to all three
   servers. A long-lived orchestrator process (or connection pool) fixes
   this without changing the MCP server code at all.
2. **Real auth (SSO/JWT) replacing the mock user dropdown.** The scoping
   logic is already tool-layer-enforced, so this is mostly swapping
   `agent_core/auth.py`'s lookup for a real identity provider call.
3. **Human-in-the-loop review queue for `needs_manager_approval` credits and
   `PREVIEW_ONLY` actions**, surfaced to staff rather than only to the
   requesting user — closes the loop on Problem 2 (trust) by making
   uncertain/high-value decisions visibly reviewable, not just blocked.
4. **Feedback loop from resolved tickets back into a "verified answers"
   layer**, distinct from the untrusted historical-resolution field —
   lets the system build genuine institutional memory over time instead of
   only ever using it as a red flag.
5. **Real vector search (embeddings) once the doc corpus grows** beyond a
   handful of files — BM25's exact-match limitation becomes a real cost at
   scale; the retriever interface is already isolated so this is a
   `retriever.py` swap, not a rewrite.
6. **Structured severity field on ticket intake** instead of the keyword
   heuristic in `sla_monitor.py`, which is a reasonable stand-in but should
   not be the long-term source of truth for something SLA-critical.
