import sys
import asyncio
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agent_core"))

from orchestrator import Orchestrator


st.set_page_config(
    page_title="ParcelPilot Support",
    page_icon="💬",
    layout="wide",
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html,body,[class*="css"]{
    font-family:'Inter',sans-serif;
}

.stApp{
    background:
        radial-gradient(circle at 15% 0%,rgba(37,99,235,.12),transparent 30%),
        radial-gradient(circle at 90% 0%,rgba(6,182,212,.08),transparent 25%),
        #060a12;
    color:#f8fafc;
}

.block-container{
    max-width:1250px;
    padding-top:1.2rem;
    padding-bottom:3rem;
}

#MainMenu,footer{
    visibility:hidden;
}

header{
    background:transparent!important;
}

.page-header{
    padding:5px 0 18px;
}

.eyebrow{
    color:#60a5fa;
    font-size:9px;
    font-weight:800;
    letter-spacing:1.7px;
}

.title{
    color:#f8fafc;
    font-size:31px;
    font-weight:800;
    letter-spacing:-1.2px;
    margin-top:5px;
}

.subtitle{
    color:#64748b;
    font-size:11px;
    line-height:1.6;
    margin-top:5px;
}

.status{
    display:inline-flex;
    align-items:center;
    gap:6px;
    padding:6px 9px;
    border-radius:999px;
    background:rgba(34,197,94,.07);
    border:1px solid rgba(34,197,94,.13);
    color:#86efac;
    font-size:8px;
    font-weight:800;
}

.dot{
    width:6px;
    height:6px;
    border-radius:50%;
    background:#22c55e;
    box-shadow:0 0 8px rgba(34,197,94,.65);
}

.chat-card{
    border:1px solid rgba(148,163,184,.08);
    border-radius:18px;
    background:rgba(8,13,23,.72);
    padding:20px;
    min-height:430px;
}

.empty{
    text-align:center;
    padding:100px 20px;
}

.empty-icon{
    font-size:35px;
}

.empty-title{
    color:#e2e8f0;
    font-size:16px;
    font-weight:750;
    margin-top:10px;
}

.empty-text{
    color:#64748b;
    font-size:10px;
    line-height:1.7;
    max-width:520px;
    margin:5px auto;
}

.info-card{
    padding:15px;
    border-radius:15px;
    background:rgba(15,23,42,.7);
    border:1px solid rgba(148,163,184,.08);
}

.info-title{
    color:#e2e8f0;
    font-size:11px;
    font-weight:750;
}

.info-text{
    color:#64748b;
    font-size:9px;
    line-height:1.55;
    margin-top:4px;
}

.user-msg{
    background:linear-gradient(135deg,#2563eb,#1d4ed8);
    color:#fff;
    padding:11px 14px;
    border-radius:14px 14px 4px 14px;
    max-width:78%;
    margin:9px 0 9px auto;
    font-size:11px;
    line-height:1.55;
}

.ai-msg{
    background:rgba(30,41,59,.62);
    color:#cbd5e1;
    padding:12px 14px;
    border-radius:14px 14px 14px 4px;
    border:1px solid rgba(148,163,184,.08);
    max-width:85%;
    margin:9px auto 9px 0;
    font-size:11px;
    line-height:1.65;
}

.tool-card{
    padding:11px 13px;
    border-radius:10px;
    background:rgba(15,23,42,.6);
    border:1px solid rgba(148,163,184,.07);
    margin-top:8px;
}

.tool-title{
    color:#94a3b8;
    font-size:9px;
    font-weight:750;
}

.tool-text{
    color:#475569;
    font-size:8px;
    margin-top:3px;
}

div[data-testid="stButton"]>button{
    min-height:39px;
    border-radius:10px;
    font-size:10px;
    font-weight:750;
    background:rgba(15,23,42,.72);
    border:1px solid rgba(148,163,184,.1);
    color:#cbd5e1;
}

div[data-testid="stButton"]>button:hover{
    border-color:rgba(96,165,250,.3);
}

.stAlert{
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)


if "messages" not in st.session_state:
    st.session_state.messages = []

if "session" not in st.session_state:
    st.session_state.session = None

if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = None


def run_turn(user_text):

    async def _go():
        orchestrator = Orchestrator()

        try:
            result = orchestrator.run_turn(
                user_text,
                session=st.session_state.session,
            )
        except TypeError:
            result = orchestrator.run_turn(user_text)

        if asyncio.iscoroutine(result):
            result = await result

        return result

    return asyncio.run(_go())


if not st.session_state.session:
    st.warning("Please sign in from the ParcelPilot home page first.")

    if st.button("← Back to ParcelPilot"):
        st.switch_page("app.py")

    st.stop()


session = st.session_state.session

account = (
    session.account_id
    if getattr(session, "account_id", None)
    else "All Accounts"
)

role = (
    "Customer"
    if getattr(session, "role", None) == "customer"
    else "Internal Support"
)


st.markdown(
    f"""
    <div class="page-header">
        <div class="eyebrow">PARCELPILOT SUPPORT INTELLIGENCE</div>
        <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
                <div class="title">Support Assistant</div>
                <div class="subtitle">
                    Evidence-aware support investigation and operational assistance.
                </div>
            </div>
            <span class="status">
                <span class="dot"></span>
                Agent Online
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


left, right = st.columns([3.1, 1], gap="large")


with right:

    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-title">Session</div>
            <div class="info-text">User: {session.display_name}</div>
            <div class="info-text">Role: {role}</div>
            <div class="info-text">Account: {account}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="info-card">
            <div class="info-title">Available capabilities</div>
            <div class="tool-card">
                <div class="tool-title">🔎 Document Search</div>
                <div class="tool-text">Policies and agreements</div>
            </div>
            <div class="tool-card">
                <div class="tool-title">📊 Operational Data</div>
                <div class="tool-text">Accounts, orders and tickets</div>
            </div>
            <div class="tool-card">
                <div class="tool-title">🧮 Business Logic</div>
                <div class="tool-text">Fees and service credits</div>
            </div>
            <div class="tool-card">
                <div class="tool-title">🔐 Protected Actions</div>
                <div class="tool-text">Confirmation before changes</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    if st.button("🧹 Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.quick_prompt = None
        st.rerun()

    if st.button("← Back", use_container_width=True):
        st.switch_page("app.py")


with left:

    st.markdown('<div class="chat-card">', unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown(
            """
            <div class="empty">
                <div class="empty-icon">🤖</div>
                <div class="empty-title">
                    How can I help?
                </div>
                <div class="empty-text">
                    Ask about an order, account, policy, cancellation,
                    service credit, support ticket or operational issue.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        for message in st.session_state.messages:

            if message["role"] == "user":
                st.markdown(
                    f'<div class="user-msg">{message["content"]}</div>',
                    unsafe_allow_html=True,
                )

            else:
                st.markdown(
                    f'<div class="ai-msg">{message["content"]}</div>',
                    unsafe_allow_html=True,
                )

    st.markdown("</div>", unsafe_allow_html=True)


prompt = st.session_state.quick_prompt

if prompt:
    st.session_state.quick_prompt = None

if not prompt:
    prompt = st.chat_input(
        "Ask ParcelPilot about an order, policy, ticket or account..."
    )


if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.spinner("ParcelPilot is investigating..."):

        try:
            result = run_turn(prompt)

            if isinstance(result, dict):

                answer = (
                    result.get("answer")
                    or result.get("response")
                    or result.get("output")
                    or result.get("message")
                )

                if answer is None:
                    answer = str(result)

            else:
                answer = str(result)

        except Exception as exc:

            error_text = str(exc)

            if "GEMINI_API_KEY" in error_text:
                answer = (
                    "The AI service is not configured on this deployment. "
                    "Please configure GEMINI_API_KEY in Streamlit Secrets."
                )
            else:
                answer = (
                    "I couldn't complete that request right now. "
                    "Please try again."
                )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

    st.rerun()
