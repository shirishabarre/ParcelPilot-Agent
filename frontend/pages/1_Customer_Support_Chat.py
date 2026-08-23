import asyncio
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "agent_core"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "components"))

from orchestrator import Orchestrator  # noqa: E402
from chat_widget import render_message, render_tool_trace  # noqa: E402
from confirm_modal import render_confirm_modal  # noqa: E402

st.set_page_config(page_title="Customer Support Chat", page_icon="💬", layout="wide")
st.title("💬 Customer Support Chat")

if "session" not in st.session_state:
    st.warning("Please log in on the main page first.")
    st.stop()

session = st.session_state["session"]
if session.role != "customer":
    st.error("This page is for customer accounts. Log in as a customer on the main page, "
             "or use Internal Ops Chat instead.")
    st.stop()

st.caption(f"Logged in as {session.display_name} — you can only see data for account `{session.account_id}`.")

if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "pending_action" not in st.session_state:
    st.session_state["pending_action"] = None


def run_turn(user_text: str):
    async def _go():
        orch = Orchestrator()
        await orch.connect()
        try:
            return await orch.run_turn(session, st.session_state["messages"], user_text)
        finally:
            await orch.aclose()
    return asyncio.run(_go())


def run_confirm(pending_action: dict):
    async def _go():
        orch = Orchestrator()
        await orch.connect()
        try:
            return await orch.execute_confirmed_action(pending_action)
        finally:
            await orch.aclose()
    return asyncio.run(_go())


for m in st.session_state["messages"]:
    render_message(m["role"], m["content"])

if st.session_state["pending_action"]:
    def _confirm():
        result = run_confirm(st.session_state["pending_action"])
        st.session_state["messages"].append({"role": "assistant", "content": f"Done — {result}"})
        st.session_state["pending_action"] = None
        st.rerun()

    def _cancel():
        st.session_state["messages"].append({"role": "assistant", "content": "Okay, I won't create that. Anything else?"})
        st.session_state["pending_action"] = None
        st.rerun()

    render_confirm_modal(st.session_state["pending_action"], _confirm, _cancel)

user_text = st.chat_input("Ask about your orders, cancellations, service credits, or support SLAs...")
if user_text:
    st.session_state["messages"].append({"role": "user", "content": user_text})
    render_message("user", user_text)
    with st.spinner("Working..."):
        result = run_turn(user_text)
    st.session_state["messages"].append({"role": "assistant", "content": result.reply})
    render_message("assistant", result.reply)
    render_tool_trace(result.tool_trace)
    if result.pending_action:
        st.session_state["pending_action"] = result.pending_action
        st.rerun()
