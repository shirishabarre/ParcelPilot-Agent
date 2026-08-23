import streamlit as st

st.set_page_config(page_title="ParcelPilot AI Support", page_icon="📦", layout="wide")

st.title("📦 ParcelPilot AI Support")
st.caption("Demo login — pick a mock user, then use the pages in the sidebar.")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent_core"))
from auth import list_demo_users, login  # noqa: E402

users = list_demo_users()
choice = st.selectbox(
    "Log in as",
    users,
    format_func=lambda u: {
        "northstar_user": "🏢 Northstar Logistics (customer, Enterprise)",
        "lumenworks_user": "🏢 LumenWorks (customer, Growth)",
        "beacon_user": "🏢 Beacon Retail (customer, Standard)",
        "rohit": "🛠️ Rohit (ParcelPilot staff)",
        "maya": "🛠️ Maya (ParcelPilot staff)",
    }.get(u, u),
)

if st.button("Log in", type="primary"):
    st.session_state["session"] = login(choice)
    st.success(f"Logged in as {st.session_state['session'].display_name}")

if "session" in st.session_state:
    s = st.session_state["session"]
    st.info(f"Currently logged in as **{s.display_name}** — role: `{s.role}`"
            + (f", account: `{s.account_id}`" if s.account_id else " (all-account access)"))
    st.markdown("Use the sidebar:\n"
                "- **Customer Support Chat** — if logged in as a customer\n"
                "- **Internal Ops Chat** — if logged in as staff\n"
                "- **Proactive Issues Dashboard** — staff-only, Problem 1")
else:
    st.warning("Log in above to continue.")
