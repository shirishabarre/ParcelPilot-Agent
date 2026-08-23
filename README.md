# ParcelPilot AI Support Agent

An MCP-based AI support system for ParcelPilot: a **customer-facing chatbot**
and an **internal support/ops chatbot**, backed by three MCP servers (tools),
a free-tier LLM, and local/free retrieval — no paid API keys anywhere.

See `docs/ARCHITECTURE.md` for the full design and `docs/DECISIONS.md` for
the reasoning behind source-precedence, access control, and confirm-before-
action. `docs/DEMO_SCRIPT.md` is the outline for the 5-minute walkthrough.

## 1. Setup

```bash
git clone <this-repo> parcelpilot-ai-agent
cd parcelpilot-ai-agent

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## 2. Get a free API key

Pick ONE (both are free tier, no card required):

- **Gemini (default)** — https://aistudio.google.com/apikey
- **Groq** — https://console.groq.com/keys

```bash
cp .env.example .env
# edit .env and paste your key into GEMINI_API_KEY (or GROQ_API_KEY + set LLM_PROVIDER=groq)
```

Load the env vars before running anything:

```bash
export $(grep -v '^#' .env | xargs)      # macOS/Linux
# or: use `python-dotenv` — already imported where needed
```

## 3. Sanity-check the data pack

```bash
python3 scripts/seed_check.py
```

## 4. Build the document search index

Run once, and again whenever a source PDF changes:

```bash
bash scripts/build_index.sh
# equivalent to: python3 mcp_servers/docs_server/ingest.py
```

## 5. Run the tests

```bash
pytest tests/ -v
# or, for the narrative end-to-end walkthrough:
python3 tests/test_scenarios.py
```

## 6. Run the app

```bash
streamlit run frontend/app.py
```

Open the URL Streamlit prints (usually http://localhost:8501), log in as one
of the mock users (customer accounts: `northstar_user`, `lumenworks_user`,
`beacon_user`; staff: `rohit`, `maya`), and use the sidebar pages.

## 7. (Debugging) Run an individual MCP server standalone

```bash
python3 mcp_servers/docs_server/server.py      # Tool 1: document search
python3 mcp_servers/data_server/server.py      # Tool 2: structured data + calculations
python3 mcp_servers/actions_server/server.py   # Tool 3: mocked state-changing actions
```

Each speaks MCP over stdio and can also be pointed to from Claude Desktop /
any MCP client using `mcp_servers.json` in this repo as the config.

## 8. (Debugging) Smoke-test the MCP client plumbing without an LLM

```bash
GEMINI_API_KEY=dummy python3 agent_core/orchestrator.py
```

This connects to all three servers, lists their tools, and runs one tool
call through the access-control override logic — useful for confirming the
MCP wiring itself before worrying about the LLM.

## 9. Run the proactive issue-detection scan (Problem 1) standalone

```bash
python3 analytics/run_daily_scan.py
```

Writes `analytics/output/issues_digest.json`, which the dashboard page
(`frontend/pages/3_Proactive_Issues_Dashboard.py`) also calls directly.

## 10. Deploy (free hosting)

**Streamlit Community Cloud** (free): push this repo to GitHub, connect it
at https://share.streamlit.io, set `frontend/app.py` as the entry point, and
add `GEMINI_API_KEY` (or `GROQ_API_KEY` + `LLM_PROVIDER`) under app secrets.
No separate backend to host — the app spawns the three MCP servers as local
subprocesses at runtime.

## Project layout

See `docs/ARCHITECTURE.md` for the annotated folder tree and data flow
diagram. Short version:

```
mcp_servers/   3 MCP servers = the 3 required tools (docs, data, actions)
agent_core/    MCP client + tool-use loop + auth + conflict/reliability logic
analytics/     Problem 1: proactive issue detection
frontend/      Streamlit chat UI (customer + internal) and dashboard
tests/         Access-control, source-precedence, calculator, and scenario tests
data/          Source PDFs/xlsx + derived index + structured contract terms
```
