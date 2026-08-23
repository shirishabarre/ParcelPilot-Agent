# 5-Minute Demo Script

## 0:00–1:00 — Architecture (talk over the diagram in docs/ARCHITECTURE.md)
- Three MCP servers = the three required tools: docs (retrieval), data
  (lookup/calc), actions (mocked, confirm-gated).
- One orchestrator = MCP client + free-tier LLM (Gemini) tool-use loop.
- Streamlit frontend, all free to host.
- One sentence each on: source-precedence file, access-control-at-tool-layer,
  confirm-before-action contract.

## 1:00–3:30 — Live demo
1. **Customer chat, Northstar user**: "Can I cancel ORD-1001 without a fee?"
   → shows tool trace: get_order → search_documents (contract surfaces) →
   calculate_cancellation → answer citing the contract, fee = 0.
2. **Same session**: "What about a shipment for LumenWorks, ORD-2001?" →
   agent should refuse/can't access (access control demo) — or just show it
   naturally doesn't offer to look it up since scoped to Northstar.
3. **Switch to LumenWorks user**: "My pickup was 4.5 hours late and it was
   the carrier's fault — do I get a credit?" → shows the fixed 300 INR
   contract override beating the default formula.
4. **Switch to staff (Rohit), internal chat**: "There's a possible API key
   exposure ticket, TKT-505 — escalate it" → shows PREVIEW_ONLY →
   confirm button → CREATED receipt. Emphasize: model could not skip the
   confirm step.
5. **Proactive dashboard**: show SLA-risk table (TKT-505 breached, TKT-501
   breached), the recurring bulk-upload cluster, and KI-208/KI-211
   correlation — "the team sees this without anyone asking."
6. *(If time)* Ask the agent about a historical ticket's guidance (TKT-450)
   to show it does NOT repeat the wrong 250 INR claim, and instead surfaces
   the correct contract-based answer.

## 3:30–4:45 — Key decisions and why
- Why MCP servers per tool (isolation, swappable, reusable outside this app).
- Why access control is enforced twice (repository + orchestrator override),
  not just prompted.
- Why numeric contract terms are extracted to YAML but full text stays
  searchable (deterministic math + still-citable evidence).
- Why BM25 instead of a hosted embedding API (free, adequate for this corpus
  size, swap point documented for scale).
- Why confirm-before-action can't be bypassed by the model itself.

## 4:45–5:00 — What's next
- Top 2–3 items from docs/DECISIONS.md's prioritized list (persistent MCP
  sessions, real auth, human review queue for high-value actions).
