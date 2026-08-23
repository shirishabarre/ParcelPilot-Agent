import streamlit as st

TOOL_ICONS = {"docs": "📄", "data": "🧮", "actions": "⚡"}
TOOL_LABELS = {"docs": "Document Search", "data": "Data Lookup / Calculation", "actions": "Action"}


def render_message(role: str, content: str):
    with st.chat_message(role):
        st.markdown(content)


def render_tool_trace(trace: list):
    """trace: list of ToolTraceEntry-like objects/dicts with server, tool, arguments, result."""
    if not trace:
        return
    with st.expander(f"🔧 {len(trace)} tool call(s) used", expanded=False):
        for entry in trace:
            server = entry.server if hasattr(entry, "server") else entry["server"]
            tool = entry.tool if hasattr(entry, "tool") else entry["tool"]
            args = entry.arguments if hasattr(entry, "arguments") else entry["arguments"]
            result = entry.result if hasattr(entry, "result") else entry["result"]
            icon = TOOL_ICONS.get(server, "🔧")
            label = TOOL_LABELS.get(server, server)
            st.markdown(f"{icon} **{label}** → `{tool}`")
            st.json({"arguments": args, "result": result}, expanded=False)
