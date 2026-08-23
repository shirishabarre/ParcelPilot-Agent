import sys
from pathlib import Path
import streamlit as st
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "agent_core"))
from auth import list_demo_users, login
st.set_page_config(page_title="ParcelPilot AI", page_icon="📦", layout="wide", initial_sidebar_state="expanded")
if "session" not in st.session_state:
    st.session_state.session = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = None
def open_chat(prompt=None):
    st.session_state.quick_prompt = prompt
    st.switch_page("pages/1_Customer_Support_Chat.py")
def clear_chat():
    st.session_state.messages = []
    st.session_state.quick_prompt = None
    st.rerun()
def logout():
    st.session_state.session = None
    st.session_state.messages = []
    st.session_state.quick_prompt = None
    st.rerun()
with st.sidebar:
    st.title("📦 ParcelPilot")
    st.caption("AI Support Intelligence")
    st.divider()
    st.subheader("Workspace")
    if st.button("💬 Support Assistant", use_container_width=True):
        open_chat()
    st.divider()
    st.subheader("System")
    st.success("Agent Online")
    st.success("RAG Available")
    st.success("MCP Tools Ready")
    if st.session_state.session:
        session = st.session_state.session
        st.divider()
        st.subheader("Authenticated Session")
        st.write(f"**User:** {session.display_name}")
        st.write(f"**Role:** {getattr(session, 'role', 'customer')}")
        account = getattr(session, "account_id", None) or "Internal Access"
        st.write(f"**Account:** {account}")
        st.divider()
        if st.button("🧹 Clear Chat", use_container_width=True):
            clear_chat()
        if st.button("↪ Sign Out", use_container_width=True):
            logout()
st.title("Intelligent support.")
st.header("Built for reliable decisions.")
st.write("""
ParcelPilot helps support teams investigate customer issues,
retrieve relevant information, check operational data and
safely handle support requests.
""")
if not st.session_state.session:
    st.divider()
    left, right = st.columns([1.2, 1], gap="large")
    with left:
        st.subheader("🤖 ParcelPilot Support Assistant")
        st.write("""
A focused AI workspace for customer support
investigation and operational assistance.
""")
        st.info("""
**Available capabilities**

🔎 Document and policy retrieval

📦 Order and ticket investigation

🧮 Business logic and calculations

🔐 Account-aware access control

🤝 Protected actions with confirmation
""")
    with right:
        st.subheader("🔐 Enter Workspace")
        st.write("Select a demo identity to authenticate.")
        users = list_demo_users()
        labels = {
            "northstar_user": "🏢 Northstar Logistics",
            "lumenworks_user": "🏢 LumenWorks",
            "beacon_user": "🏢 Beacon Retail",
            "rohit": "🛠️ Rohit - Internal Support",
            "maya": "🛠️ Maya - Internal Support",
        }
        selected_user = st.selectbox("Select identity", users, format_func=lambda user: labels.get(user, user))
        if st.button("Enter ParcelPilot →", type="primary", use_container_width=True):
            try:
                st.session_state.session = login(selected_user)
                st.session_state.messages = []
                st.session_state.quick_prompt = None
                st.rerun()
            except Exception as exc:
                st.error(f"Authentication failed: {exc}")
else:
    session = st.session_state.session
    st.success(f"Authenticated as {session.display_name}")
    st.divider()
    st.subheader("Support Actions")
    st.write("Choose a common support workflow.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("📦 Order Status")
        st.write("Investigate the current status of a customer order.")
        if st.button("Check Order", key="check_order", use_container_width=True):
            open_chat("Please investigate the current status of my order.")
    with col2:
        st.subheader("📄 Policy Search")
        st.write("Retrieve the relevant policy or support documentation.")
        if st.button("Search Policy", key="search_policy", use_container_width=True):
            open_chat("Please find the applicable policy for my issue.")
    with col3:
        st.subheader("🎫 Ticket Investigation")
        st.write("Investigate a support ticket and identify the likely next step.")
        if st.button("Investigate Ticket", key="investigate_ticket", use_container_width=True):
            open_chat("Please investigate my latest support ticket and identify the likely issue.")
    st.divider()
    st.subheader("💬 Support Assistant")
    st.write("Ask a natural-language support question.")
    if st.button("Open Support Assistant", type="primary", use_container_width=True):
        open_chat()
st.divider()
st.caption("ParcelPilot AI · Customer Support Intelligence")
