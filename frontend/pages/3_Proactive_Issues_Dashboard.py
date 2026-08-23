import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "analytics"))
from run_daily_scan import run_scan  # noqa: E402

st.set_page_config(page_title="Proactive Issues Dashboard", page_icon="📊", layout="wide")
st.title("📊 Proactive Issue Detection")
st.caption("Internal, staff-only. Surfaces SLA risk, recurring issues, known-issue correlation, and volume anomalies "
           "without waiting for someone to ask.")

if "session" not in st.session_state:
    st.warning("Please log in on the main page first.")
    st.stop()

if st.session_state["session"].role != "staff":
    st.error("Staff only.")
    st.stop()

if st.button("🔄 Run scan now"):
    st.session_state["digest"] = run_scan()

if "digest" not in st.session_state:
    st.session_state["digest"] = run_scan()

digest = st.session_state["digest"]
st.caption(f"Last scanned: {digest['generated_at']}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("SLA at risk / breached", len([r for r in digest["sla_risk"] if r["risk"] != "OK"]))
col2.metric("Recurring issue clusters", len(digest["recurring_issue_clusters"]))
col3.metric("Known-issue matches", len(digest["known_issue_correlation"]))
col4.metric("Accounts w/ volume anomaly", len(digest["volume_anomalies"]))

st.subheader("⏱️ SLA risk")
sla_df = pd.DataFrame(digest["sla_risk"])
if not sla_df.empty:
    def _highlight(row):
        color = {"BREACHED": "background-color: #ffcccc", "APPROACHING": "background-color: #fff3cd"}.get(row["risk"], "")
        return [color] * len(row)
    st.dataframe(sla_df.style.apply(_highlight, axis=1), use_container_width=True)
else:
    st.info("No open tickets.")

st.subheader("🔁 Recurring issue clusters")
if digest["recurring_issue_clusters"]:
    for c in digest["recurring_issue_clusters"]:
        badge = "🌐 multi-customer" if c["multi_customer"] else "single customer"
        st.markdown(f"**{c['cluster_subject_sample']}** — {c['count']} tickets ({badge}): "
                    f"{', '.join(c['ticket_ids'])} | accounts: {', '.join(c['accounts_involved'])}")
else:
    st.info("No recurring clusters detected.")

st.subheader("🔗 Known-issue correlation")
if digest["known_issue_correlation"]:
    for f in digest["known_issue_correlation"]:
        st.markdown(f"**{f['known_issue']} — {f['title']}** (product status: {f['product_status']}) — "
                    f"tickets: {', '.join(f['matched_tickets'])} | accounts: {', '.join(f['accounts_involved'])}\n\n"
                    f"_{f['note']}_")
else:
    st.info("No open tickets currently match a known issue.")

st.subheader("📈 Volume anomalies")
if digest["volume_anomalies"]:
    st.dataframe(pd.DataFrame(digest["volume_anomalies"]), use_container_width=True)
else:
    st.info("No account has an unusual number of open tickets right now.")
