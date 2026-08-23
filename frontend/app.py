import sys
from pathlib import Path

import streamlit as st

# ============================================================
# PATH / IMPORTS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent_core"))

from auth import list_demo_users, login


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ParcelPilot AI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PREMIUM CSS
# ============================================================

st.markdown(
    """
<style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 15% 10%,
                rgba(37, 99, 235, 0.10),
                transparent 28%
            ),
            radial-gradient(
                circle at 85% 15%,
                rgba(14, 165, 233, 0.07),
                transparent 25%
            ),
            #070b14;
        color: #f8fafc;
    }

    /* Remove default Streamlit padding */

    .block-container {
        max-width: 1450px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #0a0f1c 0%,
                #080c15 100%
            );

        border-right: 1px solid rgba(148, 163, 184, 0.10);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }

    /* =====================================================
       BRAND
       ===================================================== */

    .brand-container {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 6px 4px 20px 4px;
    }

    .brand-icon {
        width: 44px;
        height: 44px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 13px;

        background:
            linear-gradient(
                135deg,
                #2563eb,
                #0ea5e9
            );

        box-shadow:
            0 8px 30px rgba(37, 99, 235, 0.28);

        font-size: 23px;
    }

    .brand-title {
        font-size: 19px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #f8fafc;
    }

    .brand-subtitle {
        font-size: 11px;
        color: #64748b;
        margin-top: 2px;
    }

    /* =====================================================
       SIDEBAR NAV
       ===================================================== */

    .nav-label {
        color: #64748b;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin: 18px 0 8px 4px;
    }

    .nav-card {
        padding: 11px 12px;
        border-radius: 10px;
        margin-bottom: 5px;

        color: #94a3b8;
        background: transparent;

        font-size: 13px;
        font-weight: 500;
    }

    .nav-card.active {
        color: #f8fafc;

        background:
            linear-gradient(
                90deg,
                rgba(37, 99, 235, 0.18),
                rgba(37, 99, 235, 0.05)
            );

        border: 1px solid rgba(59, 130, 246, 0.18);
    }

    /* =====================================================
       STATUS CARD
       ===================================================== */

    .status-card {
        margin-top: 18px;
        padding: 15px;

        border-radius: 14px;

        background:
            rgba(15, 23, 42, 0.72);

        border:
            1px solid rgba(148, 163, 184, 0.10);

        box-shadow:
            0 15px 40px rgba(0,0,0,0.18);
    }

    .status-title {
        color: #94a3b8;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .status-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 6px 0;
    }

    .status-key {
        color: #64748b;
        font-size: 11px;
    }

    .status-value {
        color: #e2e8f0;
        font-size: 11px;
        font-weight: 600;
    }

    .online-dot {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #22c55e;
        margin-right: 6px;
        box-shadow: 0 0 10px rgba(34,197,94,0.65);
    }

    /* =====================================================
       HERO
       ===================================================== */

    .hero {
        padding: 10px 0 20px 0;
    }

    .eyebrow {
        color: #60a5fa;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .hero-title {
        font-size: 36px;
        line-height: 1.15;
        font-weight: 800;
        letter-spacing: -1.5px;
        color: #f8fafc;
        margin: 0;
    }

    .hero-description {
        color: #94a3b8;
        font-size: 14px;
        line-height: 1.7;
        margin-top: 10px;
        max-width: 760px;
    }

    /* =====================================================
       METRIC CARDS
       ===================================================== */

    .metric-card {
        padding: 18px;

        border-radius: 16px;

        background:
            linear-gradient(
                145deg,
                rgba(15, 23, 42, 0.95),
                rgba(9, 14, 25, 0.92)
            );

        border:
            1px solid rgba(148, 163, 184, 0.10);

        min-height: 110px;

        box-shadow:
            0 15px 35px rgba(0,0,0,0.16);
    }

    .metric-label {
        color: #64748b;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 22px;
        font-weight: 800;
        margin-top: 8px;
    }

    .metric-description {
        color: #64748b;
        font-size: 10px;
        margin-top: 4px;
    }

    /* =====================================================
       LOGIN PANEL
       ===================================================== */

    .login-panel {
        padding: 25px;

        border-radius: 20px;

        background:
            linear-gradient(
                145deg,
                rgba(15, 23, 42, 0.96),
                rgba(9, 14, 25, 0.94)
            );

        border:
            1px solid rgba(96, 165, 250, 0.13);

        box-shadow:
            0 25px 70px rgba(0,0,0,0.28);
    }

    .login-title {
        font-size: 20px;
        font-weight: 750;
        color: #f8fafc;
    }

    .login-description {
        font-size: 12px;
        color: #64748b;
        margin-top: 5px;
        margin-bottom: 18px;
    }

    /* =====================================================
       CHAT / CONTENT CARDS
       ===================================================== */

    .glass-card {
        padding: 20px;

        border-radius: 18px;

        background:
            rgba(15, 23, 42, 0.68);

        border:
            1px solid rgba(148, 163, 184, 0.10);

        backdrop-filter: blur(16px);

        box-shadow:
            0 20px 50px rgba(0,0,0,0.16);
    }

    .section-title {
        color: #f8fafc;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .section-description {
        color: #64748b;
        font-size: 11px;
        margin-bottom: 14px;
    }

    /* =====================================================
       TOOL BADGES
       ===================================================== */

    .tool-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
    }

    .tool-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;

        padding: 7px 10px;

        border-radius: 999px;

        background:
            rgba(30, 41, 59, 0.75);

        border:
            1px solid rgba(148, 163, 184, 0.12);

        color: #cbd5e1;

        font-size: 10px;
        font-weight: 600;
    }

    .tool-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #60a5fa;
    }

    /* =====================================================
       SECURITY BADGE
       ===================================================== */

    .security-badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;

        padding: 7px 11px;

        border-radius: 999px;

        color: #86efac;

        background:
            rgba(34, 197, 94, 0.07);

        border:
            1px solid rgba(34, 197, 94, 0.14);

        font-size: 10px;
        font-weight: 700;
    }

    /* =====================================================
       EVIDENCE CARD
       ===================================================== */

    .evidence-card {
        padding: 14px;

        border-left:
            3px solid #3b82f6;

        border-radius: 10px;

        background:
            rgba(30, 41, 59, 0.45);

        margin-top: 8px;
    }

    .evidence-source {
        color: #e2e8f0;
        font-size: 11px;
        font-weight: 700;
    }

    .evidence-meta {
        color: #64748b;
        font-size: 10px;
        margin-top: 4px;
    }

    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {
        text-align: center;
        color: #334155;
        font-size: 10px;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid rgba(148, 163, 184, 0.06);
    }

    /* =====================================================
       STREAMLIT COMPONENT OVERRIDES
       ===================================================== */

    div[data-testid="stButton"] > button {
        border-radius: 10px;
        border: 1px solid rgba(96, 165, 250, 0.20);

        background:
            linear-gradient(
                135deg,
                #2563eb,
                #1d4ed8
            );

        color: white;
        font-weight: 700;

        min-height: 42px;

        box-shadow:
            0 8px 25px rgba(37,99,235,0.18);

        transition: all 0.2s ease;
    }

    div[data-testid="stButton"] > button:hover {
        border-color: rgba(147,197,253,0.45);

        box-shadow:
            0 10px 30px rgba(37,99,235,0.28);

        transform: translateY(-1px);
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-testid="stTextArea"] textarea {
        background: #0b1220 !important;
        border: 1px solid rgba(148,163,184,0.13) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
    }

    div[data-testid="stChatInput"] {
        border-color: rgba(148,163,184,0.12);
    }

    /* Hide Streamlit menu/footer */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "session" not in st.session_state:
    st.session_state["session"] = None

if "login_attempted" not in st.session_state:
    st.session_state["login_attempted"] = False


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand-container">
            <div class="brand-icon">📦</div>
            <div>
                <div class="brand-title">ParcelPilot</div>
                <div class="brand-subtitle">AI Support Intelligence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="nav-label">Workspace</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="nav-card active">
            💬 &nbsp; Support Assistant
        </div>

        <div class="nav-card">
            🔍 &nbsp; Investigation
        </div>

        <div class="nav-card">
            📊 &nbsp; Issue Intelligence
        </div>

        <div class="nav-card">
            ⚙️ &nbsp; System Controls
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="nav-label">System</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="tool-badge">
            <span class="tool-dot"></span>
            MCP Connected
        </div>

        <div style="height:7px"></div>

        <div class="tool-badge">
            <span class="tool-dot"></span>
            RAG Available
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # USER STATUS
    # --------------------------------------------------------

    if st.session_state["session"]:

        s = st.session_state["session"]

        account_text = (
            s.account_id
            if s.account_id
            else "All accounts"
        )

        role_text = (
            "Customer"
            if s.role == "customer"
            else "Internal Staff"
        )

        st.markdown(
            f"""
            <div class="status-card">

                <div class="status-title">
                    Current Session
                </div>

                <div class="status-row">
                    <span class="status-key">User</span>
                    <span class="status-value">
                        {s.display_name}
                    </span>
                </div>

                <div class="status-row">
                    <span class="status-key">Role</span>
                    <span class="status-value">
                        {role_text}
                    </span>
                </div>

                <div class="status-row">
                    <span class="status-key">Account</span>
                    <span class="status-value">
                        {account_text}
                    </span>
                </div>

                <div style="margin-top:10px">
                    <span class="security-badge">
                        <span class="online-dot"></span>
                        Secure session
                    </span>
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# MAIN HERO
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="eyebrow">
            PARCELPILOT INTELLIGENCE PLATFORM
        </div>

        <div class="hero-title">
            AI-powered support,<br>
            built for reliable decisions.
        </div>

        <div class="hero-description">
            Investigate customer issues, retrieve authoritative
            documentation, calculate deterministic outcomes and
            safely execute operational actions through an MCP-powered
            agent architecture.
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TOP METRICS
# ============================================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Agent Status</div>
            <div class="metric-value">
                <span style="color:#4ade80">●</span> Online
            </div>
            <div class="metric-description">
                Orchestrator ready
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Retrieval</div>
            <div class="metric-value">RAG</div>
            <div class="metric-description">
                Policy-aware document search
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Tool Layer</div>
            <div class="metric-value">3 MCP</div>
            <div class="metric-description">
                Docs · Data · Actions
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Safety</div>
            <div class="metric-value">HITL</div>
            <div class="metric-description">
                Human confirmation for actions
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)


# ============================================================
# LOGIN / SESSION
# ============================================================

if not st.session_state["session"]:

    left, right = st.columns([1.35, 1])

    # --------------------------------------------------------
    # LEFT
    # --------------------------------------------------------

    with left:

        st.markdown(
            """
            <div class="glass-card">

                <div class="section-title">
                    Intelligent Support Workspace
                </div>

                <div class="section-description">
                    Select a demo identity to enter the
                    ParcelPilot AI environment.
                </div>

                <div class="tool-row">

                    <div class="tool-badge">
                        🔎 Document Retrieval
                    </div>

                    <div class="tool-badge">
                        🧮 Deterministic Calculations
                    </div>

                    <div class="tool-badge">
                        🔐 Account Isolation
                    </div>

                    <div class="tool-badge">
                        🤝 Human-in-the-loop
                    </div>

                </div>

                <div style="height:18px"></div>

                <div class="evidence-card">

                    <div class="evidence-source">
                        Why ParcelPilot AI?
                    </div>

                    <div class="evidence-meta">
                        The assistant does more than generate text.
                        It retrieves evidence, applies business rules,
                        respects account boundaries and requires
                        confirmation before state-changing actions.
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # RIGHT
    # --------------------------------------------------------

    with right:

        st.markdown(
            """
            <div class="login-panel">

                <div class="login-title">
                    🔐 Secure Demo Login
                </div>

                <div class="login-description">
                    Choose an authenticated identity.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        users = list_demo_users()

        choice = st.selectbox(
            "Demo identity",
            users,
            label_visibility="collapsed",
            format_func=lambda u: {
                "northstar_user":
                    "🏢 Northstar Logistics · Enterprise",

                "lumenworks_user":
                    "🏢 LumenWorks · Growth",

                "beacon_user":
                    "🏢 Beacon Retail · Standard",

                "rohit":
                    "🛠️ Rohit · Internal Support",

                "maya":
                    "🛠️ Maya · Internal Support",
            }.get(u, u),
        )

        if st.button(
            "Enter ParcelPilot",
            type="primary",
            use_container_width=True,
        ):

            try:

                st.session_state["session"] = login(choice)
                st.session_state["login_attempted"] = True

                st.rerun()

            except Exception as e:

                st.error(str(e))


else:

    # ========================================================
    # LOGGED-IN EXPERIENCE
    # ========================================================

    s = st.session_state["session"]

    # --------------------------------------------------------
    # ACCOUNT HEADER
    # --------------------------------------------------------

    account_name = (
        s.account_id
        if s.account_id
        else "All Accounts"
    )

    role_name = (
        "Customer"
        if s.role == "customer"
        else "Internal Operations"
    )

    left, right = st.columns([3, 1])

    with left:

        st.markdown(
            f"""
            <div class="glass-card">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                ">

                    <div>

                        <div class="section-title">
                            Welcome back, {s.display_name}
                        </div>

                        <div class="section-description">
                            {role_name} · {account_name}
                        </div>

                    </div>

                    <div class="security-badge">
                        <span class="online-dot"></span>
                        Authenticated
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:

        if st.button(
            "Sign out",
            use_container_width=True,
        ):

            st.session_state["session"] = None
            st.rerun()

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # AGENT CAPABILITIES
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="glass-card">

            <div class="section-title">
                Agent Capabilities
            </div>

            <div class="section-description">
                Available capabilities for this authenticated session.
            </div>

            <div class="tool-row">

                <div class="tool-badge">
                    <span class="tool-dot"></span>
                    Document Search
                </div>

                <div class="tool-badge">
                    <span class="tool-dot"></span>
                    Account Lookup
                </div>

                <div class="tool-badge">
                    <span class="tool-dot"></span>
                    Order Investigation
                </div>

                <div class="tool-badge">
                    <span class="tool-dot"></span>
                    Ticket Analysis
                </div>

                <div class="tool-badge">
                    <span class="tool-dot"></span>
                    Cancellation Calculation
                </div>

                <div class="tool-badge">
                    <span class="tool-dot"></span>
                    Service Credit
                </div>

                <div class="tool-badge">
                    <span class="tool-dot"></span>
                    Safe Actions
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # QUICK ACTIONS
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="section-title">
            What would you like to investigate?
        </div>

        <div class="section-description">
            Start with a natural-language request.
        </div>
        """,
        unsafe_allow_html=True,
    )

    q1, q2, q3 = st.columns(3)

    with q1:

        st.markdown(
            """
            <div class="glass-card">

                <div style="font-size:22px">
                    📦
                </div>

                <div class="section-title" style="margin-top:8px">
                    Track an Order
                </div>

                <div class="section-description">
                    Investigate order status,
                    delivery issues and account context.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with q2:

        st.markdown(
            """
            <div class="glass-card">

                <div style="font-size:22px">
                    📄
                </div>

                <div class="section-title" style="margin-top:8px">
                    Check a Policy
                </div>

                <div class="section-description">
                    Search authoritative agreements,
                    SOPs and operational documentation.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with q3:

        st.markdown(
            """
            <div class="glass-card">

                <div style="font-size:22px">
                    🧮
                </div>

                <div class="section-title" style="margin-top:8px">
                    Calculate an Outcome
                </div>

                <div class="section-description">
                    Determine cancellation fees,
                    credits and escalation requirements.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # CHAT PLACEHOLDER
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="glass-card">

            <div class="section-title">
                💬 Support Assistant
            </div>

            <div class="section-description">
                Ask ParcelPilot AI about an order, account,
                ticket, policy or operational issue.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # This is where your existing chat/page navigation
    # can continue to operate.

    user_message = st.chat_input(
        "Ask ParcelPilot AI anything about your account..."
    )

    if user_message:

        with st.chat_message("user"):
            st.write(user_message)

        with st.chat_message("assistant"):

            st.markdown(
                """
                <div class="evidence-card">

                    <div class="evidence-source">
                        🤖 Agent ready
                    </div>

                    <div class="evidence-meta">
                        Your request has been received.
                        Connect this area to your existing
                        Orchestrator.run_turn() implementation.
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    # --------------------------------------------------------
    # SECURITY / ARCHITECTURE PANEL
    # --------------------------------------------------------

    st.markdown("<div style='height:25px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            <div class="glass-card">

                <div class="section-title">
                    🔐 Security Context
                </div>

                <div class="section-description">
                    Authorization is derived from the
                    authenticated session rather than user text.
                </div>

                <div class="evidence-card">

                    <div class="evidence-source">
                        Tenant Isolation
                    </div>

                    <div class="evidence-meta">
                        Customer requests are restricted
                        to their authenticated account.
                    </div>

                </div>

                <div class="evidence-card">

                    <div class="evidence-source">
                        Action Protection
                    </div>

                    <div class="evidence-meta">
                        State-changing operations require
                        preview → explicit confirmation → execution.
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            """
            <div class="glass-card">

                <div class="section-title">
                    🧠 Reliability Layer
                </div>

                <div class="section-description">
                    Answers are designed around authoritative
                    evidence and deterministic business logic.
                </div>

                <div class="evidence-card">

                    <div class="evidence-source">
                        Source Precedence
                    </div>

                    <div class="evidence-meta">
                        Customer agreement → current policy →
                        product documentation → historical context.
                    </div>

                </div>

                <div class="evidence-card">

                    <div class="evidence-source">
                        Conflict Detection
                    </div>

                    <div class="evidence-meta">
                        Low-confidence retrieval and missing
                        verification data trigger escalation.
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        ParcelPilot AI Support · MCP Agent Architecture ·
        Retrieval-Augmented Generation · Human-in-the-loop Actions
    </div>
    """,
    unsafe_allow_html=True,
)
