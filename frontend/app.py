import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "agent_core"))

from auth import list_demo_users, login


st.set_page_config(
    page_title="ParcelPilot AI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    .stApp {
        background: #0b1120;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
    }

    section[data-testid="stSidebar"] {
        background: #080d18;
        border-right: 1px solid #1e293b;
    }

    .brand {
        font-size: 22px;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 4px;
    }

    .brand-subtitle {
        color: #64748b;
        font-size: 11px;
        margin-bottom: 30px;
    }

    .hero-title {
        font-size: 38px;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.15;
    }

    .hero-title span {
        color: #60a5fa;
    }

    .hero-text {
        color: #94a3b8;
        font-size: 14px;
        line-height: 1.7;
        max-width: 720px;
        margin-top: 12px;
        margin-bottom: 30px;
    }

    .card {
        background: #111827;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 16px;
    }

    .card-title {
        color: #f8fafc;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .card-text {
        color: #94a3b8;
        font-size: 13px;
        line-height: 1.6;
    }

    .feature {
        color: #cbd5e1;
        font-size: 13px;
        padding: 7px 0;
    }

    .section-title {
        color: #f8fafc;
        font-size: 20px;
        font-weight: 600;
        margin: 25px 0 12px;
    }

    .status {
        background: #111827;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 8px;
        color: #94a3b8;
        font-size: 12px;
    }

    .dot {
        color: #22c55e;
    }

    .session {
        background: #111827;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 14px;
        margin-top: 20px;
    }

    .session-title {
        color: #64748b;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }

    .session-row {
        color: #cbd5e1;
        font-size: 12px;
        margin: 6px 0;
    }

    .footer {
        text-align: center;
        color: #475569;
        font-size: 11px;
        margin-top: 40px;
    }

    div[data-testid="stButton"] > button {
        border-radius: 8px;
        min-height: 40px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


if "session" not in st.session_state:
    st.session_state.session = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = None


def open_chat(prompt=None):
    st.session_state.quick_prompt = prompt
    st.switch_page("pages/1_Customer_Support_Chat.py")


def clear_session():
    st.session_state.session = None
    st.session_state.messages = []
    st.session_state.quick_prompt = None
    st.rerun()


with st.sidebar:
    st.markdown(
        """
        <div class="brand">📦 ParcelPilot</div>
        <div class="brand-subtitle">AI SUPPORT INTELLIGENCE</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Workspace")

    if st.button(
        "💬 Support Assistant",
        use_container_width=True,
    ):
        open_chat()

    st.markdown("### System")

    st.markdown(
        """
        <div class="status">
            <span class="dot">●</span> Agent Online
        </div>

        <div class="status">
            <span class="dot">●</span> RAG Available
        </div>

        <div class="status">
            <span class="dot">●</span> MCP Tools Ready
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.session:
        session = st.session_state.session

        role = getattr(session, "role", "customer")

        account = (
            getattr(session, "account_id", None)
            or "Internal Access"
        )

        st.markdown(
            f"""
            <div class="session">
                <div class="session-title">
                    AUTHENTICATED SESSION
                </div>

                <div class="session-row">
                    👤 {session.display_name}
                </div>

                <div class="session-row">
                    🔐 {role}
                </div>

                <div class="session-row">
                    🏢 {account}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("")

        if st.button(
            "🧹 Clear Chat",
            use_container_width=True,
        ):
            st.session_state.messages = []
            st.session_state.quick_prompt = None
            st.rerun()

        if st.button(
            "↪ Sign Out",
            use_container_width=True,
        ):
            clear_session()


st.markdown(
    """
    <div class="hero-title">
        Intelligent support.<br>
        <span>Built for reliable decisions.</span>
    </div>

    <div class="hero-text">
        ParcelPilot helps support teams investigate customer
        issues, retrieve relevant information, check operational
        data and safely handle support requests.
    </div>
    """,
    unsafe_allow_html=True,
)


if not st.session_state.session:

    left, right = st.columns(
        [1.25, 1],
        gap="large",
    )

    with left:
        st.markdown(
            """
            <div class="card">
                <div class="card-title">
                    🤖 ParcelPilot Support Assistant
                </div>

                <div class="card-text">
                    A simple AI workspace for customer support
                    investigation and operational assistance.
                </div>

                <br>

                <div class="feature">
                    🔎 Document and policy retrieval
                </div>

                <div class="feature">
                    📦 Order and ticket investigation
                </div>

                <div class="feature">
                    🧮 Business logic and calculations
                </div>

                <div class="feature">
                    🔐 Account-aware access control
                </div>

                <div class="feature">
                    🤝 Protected actions with confirmation
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="card">
                <div class="card-title">
                    🔐 Enter Workspace
                </div>

                <div class="card-text">
                    Select a demo identity to authenticate.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        users = list_demo_users()

        labels = {
            "northstar_user":
                "🏢 Northstar Logistics",
            "lumenworks_user":
                "🏢 LumenWorks",
            "beacon_user":
                "🏢 Beacon Retail",
            "rohit":
                "🛠️ Rohit · Internal Support",
            "maya":
                "🛠️ Maya · Internal Support",
        }

        selected_user = st.selectbox(
            "Select identity",
            users,
            format_func=lambda x: labels.get(x, x),
        )

        if st.button(
            "Enter ParcelPilot →",
            type="primary",
            use_container_width=True,
        ):
            try:
                st.session_state.session = login(
                    selected_user
                )

                st.session_state.messages = []
                st.session_state.quick_prompt = None

                st.rerun()

            except Exception as exc:
                st.error(
                    f"Unable to authenticate: {exc}"
                )


else:

    session = st.session_state.session

    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">
                Welcome, {session.display_name} 👋
            </div>

            <div class="card-text">
                You are authenticated and ready to use
                the ParcelPilot Support Assistant.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Support Actions</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="card">
                <div class="card-title">
                    📦 Order Status
                </div>

                <div class="card-text">
                    Check the current status of
                    a customer order.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Check Order",
            key="order",
            use_container_width=True,
        ):
            open_chat(
                "Please investigate the current status of my order."
            )

    with col2:
        st.markdown(
            """
            <div class="card">
                <div class="card-title">
                    📄 Policy Search
                </div>

                <div class="card-text">
                    Retrieve the relevant policy
                    or support documentation.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Search Policy",
            key="policy",
            use_container_width=True,
        ):
            open_chat(
                "Please find the applicable policy for my issue."
            )

    with col3:
        st.markdown(
            """
            <div class="card">
                <div class="card-title">
                    🎫 Ticket Investigation
                </div>

                <div class="card-text">
                    Investigate a support ticket
                    and identify the next step.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Investigate Ticket",
            key="ticket",
            use_container_width=True,
        ):
            open_chat(
                "Please investigate my latest support ticket and identify the likely issue."
            )

    st.markdown("")

    if st.button(
        "💬 Open Support Assistant",
        type="primary",
        use_container_width=True,
    ):
        open_chat()


st.markdown(
    """
    <div class="footer">
        ParcelPilot AI · Customer Support Intelligence
    </div>
    """,
    unsafe_allow_html=True,
)
