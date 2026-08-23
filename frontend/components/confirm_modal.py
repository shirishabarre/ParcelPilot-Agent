import streamlit as st


def render_confirm_modal(pending_action: dict, on_confirm, on_cancel):
    """
    pending_action: {"tool": str, "arguments": dict, "preview": dict}
    on_confirm / on_cancel: zero-arg callables.
    """
    preview = pending_action["preview"]
    st.warning("⚠️ Action requires your confirmation before it's created:")
    st.json(preview.get("would_create") or preview.get("would_update") or preview, expanded=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirm and execute", type="primary", use_container_width=True):
            on_confirm()
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            on_cancel()
