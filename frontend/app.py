import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html,body,[class*="css"]{
    font-family:'Inter',sans-serif;
}

.stApp{
    background:
        radial-gradient(circle at 10% 0%,rgba(37,99,235,.13),transparent 28%),
        radial-gradient(circle at 90% 5%,rgba(14,165,233,.09),transparent 25%),
        radial-gradient(circle at 50% 100%,rgba(59,130,246,.05),transparent 35%),
        #060a12;
    color:#f8fafc;
}

.block-container{
    max-width:1480px;
    padding-top:1.4rem;
    padding-bottom:4rem;
}

section[data-testid="stSidebar"]{
    background:
        linear-gradient(180deg,#080d18 0%,#060a12 100%);
    border-right:1px solid rgba(148,163,184,.09);
}

section[data-testid="stSidebar"]>div{
    padding-top:1.2rem;
}

#MainMenu,footer{
    visibility:hidden;
}

header{
    background:transparent!important;
}

.brand{
    display:flex;
    align-items:center;
    gap:12px;
    padding:8px 5px 22px;
}

.brand-icon{
    width:46px;
    height:46px;
    border-radius:14px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:linear-gradient(135deg,#2563eb,#06b6d4);
    box-shadow:0 12px 35px rgba(37,99,235,.3);
    font-size:23px;
}

.brand-title{
    font-size:19px;
    font-weight:800;
    color:#f8fafc;
    letter-spacing:-.5px;
}

.brand-subtitle{
    font-size:10px;
    color:#64748b;
    margin-top:2px;
}

.sidebar-label{
    color:#475569;
    font-size:10px;
    font-weight:800;
    letter-spacing:1.2px;
    text-transform:uppercase;
    margin:18px 4px 8px;
}

.sidebar-info{
    padding:13px;
    border:1px solid rgba(148,163,184,.08);
    border-radius:13px;
    background:rgba(15,23,42,.6);
    margin-top:15px;
}

.sidebar-row{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin:8px 0;
}

.sidebar-key{
    color:#64748b;
    font-size:10px;
}

.sidebar-value{
    color:#cbd5e1;
    font-size:10px;
    font-weight:700;
}

.online{
    display:inline-flex;
    align-items:center;
    gap:6px;
    padding:6px 9px;
    border-radius:999px;
    color:#86efac;
    background:rgba(34,197,94,.07);
    border:1px solid rgba(34,197,94,.14);
    font-size:9px;
    font-weight:800;
}

.dot{
    width:6px;
    height:6px;
    border-radius:50%;
    background:#22c55e;
    box-shadow:0 0 9px rgba(34,197,94,.7);
}

.system-pill{
    display:flex;
    align-items:center;
    gap:7px;
    padding:8px 10px;
    margin:6px 0;
    border-radius:9px;
    background:rgba(15,23,42,.65);
    border:1px solid rgba(148,163,184,.07);
    color:#94a3b8;
    font-size:10px;
}

.system-dot{
    width:6px;
    height:6px;
    border-radius:50%;
    background:#38bdf8;
    box-shadow:0 0 8px rgba(56,189,248,.7);
}

.hero{
    padding:7px 0 22px;
}

.eyebrow{
    color:#60a5fa;
    font-size:10px;
    font-weight:800;
    letter-spacing:1.8px;
    text-transform:uppercase;
    margin-bottom:8px;
}

.hero-title{
    font-size:39px;
    line-height:1.08;
    font-weight:800;
    letter-spacing:-1.8px;
    margin:0;
    color:#f8fafc;
}

.hero-title span{
    background:linear-gradient(90deg,#60a5fa,#22d3ee);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

.hero-text{
    max-width:760px;
    color:#64748b;
    font-size:13px;
    line-height:1.7;
    margin-top:10px;
}

.metric{
    min-height:108px;
    padding:17px;
    border-radius:16px;
    background:
        linear-gradient(145deg,rgba(15,23,42,.9),rgba(8,13,23,.92));
    border:1px solid rgba(148,163,184,.09);
    box-shadow:0 18px 45px rgba(0,0,0,.15);
}

.metric-label{
    color:#475569;
    font-size:9px;
    font-weight:800;
    letter-spacing:1px;
    text-transform:uppercase;
}

.metric-value{
    color:#f8fafc;
    font-size:21px;
    font-weight:800;
    margin-top:8px;
}

.metric-sub{
    color:#64748b;
    font-size:9px;
    margin-top:4px;
}

.card{
    padding:19px;
    border-radius:18px;
    background:
        linear-gradient(145deg,rgba(15,23,42,.82),rgba(8,13,23,.72));
    border:1px solid rgba(148,163,184,.09);
    box-shadow:0 20px 55px rgba(0,0,0,.14);
    backdrop-filter:blur(18px);
}

.card-title{
    color:#f8fafc;
    font-size:14px;
    font-weight:750;
}

.card-subtitle{
    color:#64748b;
    font-size:10px;
    line-height:1.6;
    margin-top:4px;
}

.capability{
    display:inline-flex;
    align-items:center;
    gap:6px;
    padding:7px 10px;
    border-radius:999px;
    background:rgba(30,41,59,.6);
    border:1px solid rgba(148,163,184,.09);
    color:#cbd5e1;
    font-size:9px;
    font-weight:650;
    margin:4px 4px 0 0;
}

.cap-dot{
    width:5px;
    height:5px;
    border-radius:50%;
    background:#60a5fa;
}

.quick-card{
    padding:17px;
    min-height:155px;
    border-radius:17px;
    background:
        linear-gradient(145deg,rgba(15,23,42,.88),rgba(8,13,23,.72));
    border:1px solid rgba(148,163,184,.08);
    transition:.2s ease;
}

.quick-icon{
    font-size:24px;
    margin-bottom:9px;
}

.quick-title{
    color:#f8fafc;
    font-size:13px;
    font-weight:750;
}

.quick-text{
    color:#64748b;
    font-size:10px;
    line-height:1.55;
    margin-top:5px;
}

.section-label{
    color:#f8fafc;
    font-size:15px;
    font-weight:750;
    margin-bottom:4px;
}

.section-sub{
    color:#64748b;
    font-size:10px;
    margin-bottom:12px;
}

.login-box{
    padding:24px;
    border-radius:20px;
    background:
        linear-gradient(145deg,rgba(15,23,42,.96),rgba(7,12,22,.93));
    border:1px solid rgba(96,165,250,.13);
    box-shadow:0 30px 80px rgba(0,0,0,.3);
}

.login-title{
    font-size:20px;
    font-weight:800;
    color:#f8fafc;
}

.login-sub{
    color:#64748b;
    font-size:10px;
    line-height:1.6;
    margin-top:5px;
    margin-bottom:16px;
}

.feature{
    padding:12px;
    border-radius:12px;
    background:rgba(15,23,42,.55);
    border:1px solid rgba(148,163,184,.07);
    margin-top:8px;
}

.feature-title{
    color:#cbd5e1;
    font-size:10px;
    font-weight:750;
}

.feature-text{
    color:#64748b;
    font-size:9px;
    line-height:1.5;
    margin-top:3px;
}

.chat-shell{
    border:1px solid rgba(148,163,184,.09);
    border-radius:19px;
    background:rgba(8,13,23,.66);
    padding:19px;
    min-height:230px;
}

.empty-chat{
    text-align:center;
    padding:42px 20px 34px;
}

.empty-icon{
    font-size:36px;
    margin-bottom:10px;
}

.empty-title{
    color:#e2e8f0;
    font-size:16px;
    font-weight:750;
}

.empty-text{
    color:#64748b;
    max-width:520px;
    margin:6px auto 0;
    font-size:10px;
    line-height:1.7;
}

.message-user{
    background:linear-gradient(135deg,#1d4ed8,#2563eb);
    color:#fff;
    padding:12px 15px;
    border-radius:15px 15px 4px 15px;
    margin:8px 0 8px auto;
    max-width:80%;
    font-size:12px;
}

.message-assistant{
    background:rgba(30,41,59,.62);
    color:#cbd5e1;
    padding:13px 15px;
    border-radius:15px 15px 15px 4px;
    border:1px solid rgba(148,163,184,.08);
    margin:8px auto 8px 0;
    max-width:86%;
    font-size:12px;
    line-height:1.6;
}

.evidence{
    padding:13px;
    border-left:3px solid #3b82f6;
    border-radius:9px;
    background:rgba(30,41,59,.38);
    margin-top:10px;
}

.evidence-title{
    color:#e2e8f0;
    font-size:10px;
    font-weight:750;
}

.evidence-text{
    color:#64748b;
    font-size:9px;
    line-height:1.55;
    margin-top:3px;
}

.footer{
    text-align:center;
    color:#334155;
    font-size:9px;
    margin-top:45px;
    padding-top:20px;
    border-top:1px solid rgba(148,163,184,.05);
}

div[data-testid="stButton"]>button{
    min-height:40px;
    border-radius:10px;
    border:1px solid rgba(96,165,250,.18);
    background:linear-gradient(135deg,#2563eb,#1d4ed8);
    color:#fff;
    font-size:11px;
    font-weight:750;
    box-shadow:0 8px 25px rgba(37,99,235,.14);
    transition:.2s ease;
}

div[data-testid="stButton"]>button:hover{
    border-color:rgba(147,197,253,.4);
    box-shadow:0 10px 30px rgba(37,99,235,.25);
    transform:translateY(-1px);
}

div[data-testid="stButton"]>button[kind="secondary"]{
    background:rgba(15,23,42,.72);
    border-color:rgba(148,163,184,.1);
    color:#cbd5e1;
    box-shadow:none;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] div[data-baseweb="select"]{
    background:#0b1220!important;
    border:1px solid rgba(148,163,184,.11)!important;
    border-radius:10px!important;
    color:#e2e8f0!important;
}

div[data-testid="stChatInput"]{
    border-color:rgba(148,163,184,.1);
}

.stAlert{
    border-radius:11px;
}

hr{
    border-color:rgba(148,163,184,.06);
}
</style>
""",
    unsafe_allow_html=True,
)

if "session" not in st.session_state:
    st.session_state.session = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "active_view" not in st.session_state:
    st.session_state.active_view = "Support Assistant"


def set_prompt(prompt):
    st.session_state.pending_prompt = prompt
    st.rerun()


def clear_conversation():
    st.session_state.messages = []
    st.session_state.pending_prompt = None
    st.rerun()


def sign_out():
    st.session_state.session = None
    st.session_state.messages = []
    st.session_state.pending_prompt = None
    st.rerun()


with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">📦</div>
            <div>
                <div class="brand-title">ParcelPilot</div>
                <div class="brand-subtitle">AI SUPPORT INTELLIGENCE</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-label">Workspace</div>', unsafe_allow_html=True)

    if st.button(
        "💬  Support Assistant",
        use_container_width=True,
        type="primary" if st.session_state.active_view == "Support Assistant" else "secondary",
    ):
        st.session_state.active_view = "Support Assistant"
        st.rerun()

    if st.button(
        "🔎  Investigation",
        use_container_width=True,
        type="primary" if st.session_state.active_view == "Investigation" else "secondary",
    ):
        st.session_state.active_view = "Investigation"
        set_prompt("Investigate the current customer issue and identify the most likely cause.")

    if st.button(
        "📊  Issue Intelligence",
        use_container_width=True,
        type="primary" if st.session_state.active_view == "Issue Intelligence" else "secondary",
    ):
        st.session_state.active_view = "Issue Intelligence"
        set_prompt("Analyze the current issue and provide the relevant evidence, risks and recommended next steps.")

    if st.button(
        "⚙️  System Controls",
        use_container_width=True,
        type="primary" if st.session_state.active_view == "System Controls" else "secondary",
    ):
        st.session_state.active_view = "System Controls"
        set_prompt("Show the available operational capabilities and explain which actions require human confirmation.")

    st.markdown('<div class="sidebar-label">System</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="system-pill">
            <span class="system-dot"></span>
            MCP Connected
        </div>
        <div class="system-pill">
            <span class="system-dot"></span>
            RAG Available
        </div>
        <div class="system-pill">
            <span class="system-dot"></span>
            Agent Online
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.session:
        s = st.session_state.session
        account = s.account_id if s.account_id else "All Accounts"
        role = "Customer" if s.role == "customer" else "Internal Staff"

        st.markdown(
            f"""
            <div class="sidebar-info">
                <div class="sidebar-row">
                    <span class="sidebar-key">User</span>
                    <span class="sidebar-value">{s.display_name}</span>
                </div>
                <div class="sidebar-row">
                    <span class="sidebar-key">Role</span>
                    <span class="sidebar-value">{role}</span>
                </div>
                <div class="sidebar-row">
                    <span class="sidebar-key">Account</span>
                    <span class="sidebar-value">{account}</span>
                </div>
                <div style="margin-top:11px">
                    <span class="online">
                        <span class="dot"></span>
                        Secure session
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        if st.button("🧹  Clear Conversation", use_container_width=True, type="secondary"):
            clear_conversation()

        if st.button("↪  Sign Out", use_container_width=True, type="secondary"):
            sign_out()


st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">PARCELPILOT INTELLIGENCE PLATFORM</div>
        <div class="hero-title">
            Reliable support.<br>
            <span>Intelligent decisions.</span>
        </div>
        <div class="hero-text">
            Investigate customer issues, retrieve authoritative documentation,
            calculate deterministic outcomes and safely execute operational
            actions through an MCP-powered AI support environment.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        """
        <div class="metric">
            <div class="metric-label">Agent Status</div>
            <div class="metric-value">● Online</div>
            <div class="metric-sub">Orchestrator ready</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m2:
    st.markdown(
        """
        <div class="metric">
            <div class="metric-label">Retrieval</div>
            <div class="metric-value">RAG</div>
            <div class="metric-sub">Evidence-aware search</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        """
        <div class="metric">
            <div class="metric-label">Tool Layer</div>
            <div class="metric-value">3 MCP</div>
            <div class="metric-sub">Docs · Data · Actions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m4:
    st.markdown(
        """
        <div class="metric">
            <div class="metric-label">Safety</div>
            <div class="metric-value">HITL</div>
            <div class="metric-sub">Protected actions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

if not st.session_state.session:
    left, right = st.columns([1.35, 1], gap="large")

    with left:
        st.markdown(
            """
            <div class="card">
                <div class="card-title">Intelligent Support Workspace</div>
                <div class="card-subtitle">
                    A secure AI workspace for customer support investigation,
                    evidence retrieval and operational decision-making.
                </div>

                <div style="height:13px"></div>

                <span class="capability">🔎 Document Retrieval</span>
                <span class="capability">🧮 Deterministic Logic</span>
                <span class="capability">🔐 Account Isolation</span>
                <span class="capability">🤝 Human Approval</span>

                <div style="height:15px"></div>

                <div class="feature">
                    <div class="feature-title">Evidence-first answers</div>
                    <div class="feature-text">
                        Retrieve relevant policies, agreements and operational
                        documentation before producing a response.
                    </div>
                </div>

                <div class="feature">
                    <div class="feature-title">Account-aware intelligence</div>
                    <div class="feature-text">
                        Requests are evaluated using the authenticated session
                        rather than relying on account information supplied by text.
                    </div>
                </div>

                <div class="feature">
                    <div class="feature-title">Safe operational actions</div>
                    <div class="feature-text">
                        State-changing actions can follow a preview,
                        confirmation and execution workflow.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="login-box">
                <div class="login-title">🔐 Secure Demo Login</div>
                <div class="login-sub">
                    Choose an authenticated identity to enter the ParcelPilot
                    intelligence workspace.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        users = list_demo_users()

        labels = {
            "northstar_user": "🏢 Northstar Logistics · Enterprise",
            "lumenworks_user": "🏢 LumenWorks · Growth",
            "beacon_user": "🏢 Beacon Retail · Standard",
            "rohit": "🛠️ Rohit · Internal Support",
            "maya": "🛠️ Maya · Internal Support",
        }

        choice = st.selectbox(
            "Demo identity",
            users,
            format_func=lambda x: labels.get(x, x),
            label_visibility="collapsed",
        )

        st.markdown("<div style='height:7px'></div>", unsafe_allow_html=True)

        if st.button(
            "Enter ParcelPilot  →",
            type="primary",
            use_container_width=True,
        ):
            try:
                st.session_state.session = login(choice)
                st.session_state.messages = []
                st.rerun()
            except Exception as e:
                st.error(str(e))

else:
    s = st.session_state.session

    account_name = s.account_id if s.account_id else "All Accounts"
    role_name = "Customer" if s.role == "customer" else "Internal Operations"

    h1, h2 = st.columns([3.3, 1])

    with h1:
        st.markdown(
            f"""
            <div class="card">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                        <div class="card-title">Welcome back, {s.display_name}</div>
                        <div class="card-subtitle">{role_name} · {account_name}</div>
                    </div>
                    <span class="online">
                        <span class="dot"></span>
                        Authenticated
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with h2:
        if st.button("↪ Sign Out", use_container_width=True, type="secondary"):
            sign_out()

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="card">
            <div class="card-title">Agent Capabilities</div>
            <div class="card-subtitle">
                Capabilities available in your authenticated support session.
            </div>
            <div style="margin-top:8px">
                <span class="capability"><span class="cap-dot"></span>Document Search</span>
                <span class="capability"><span class="cap-dot"></span>Account Lookup</span>
                <span class="capability"><span class="cap-dot"></span>Order Investigation</span>
                <span class="capability"><span class="cap-dot"></span>Ticket Analysis</span>
                <span class="capability"><span class="cap-dot"></span>Cancellation Calculation</span>
                <span class="capability"><span class="cap-dot"></span>Service Credit</span>
                <span class="capability"><span class="cap-dot"></span>Protected Actions</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="section-label">What would you like to investigate?</div>
        <div class="section-sub">
            Use a quick action or ask the assistant directly.
        </div>
        """,
        unsafe_allow_html=True,
    )

    q1, q2, q3 = st.columns(3)

    with q1:
        st.markdown(
            """
            <div class="quick-card">
                <div class="quick-icon">📦</div>
                <div class="quick-title">Track an Order</div>
                <div class="quick-text">
                    Investigate order status, delivery issues and
                    account context.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Track Order", key="track_order", use_container_width=True):
            set_prompt("Track my order and investigate its current delivery status.")

    with q2:
        st.markdown(
            """
            <div class="quick-card">
                <div class="quick-icon">📄</div>
                <div class="quick-title">Check a Policy</div>
                <div class="quick-text">
                    Search agreements, SOPs and authoritative
                    operational documentation.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Check Policy", key="check_policy", use_container_width=True):
            set_prompt("Check the relevant policy for my current issue and cite the supporting evidence.")

    with q3:
        st.markdown(
            """
            <div class="quick-card">
                <div class="quick-icon">🧮</div>
                <div class="quick-title">Calculate Outcome</div>
                <div class="quick-text">
                    Determine cancellation fees, credits and
                    escalation requirements.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Calculate Outcome", key="calculate", use_container_width=True):
            set_prompt("Calculate the applicable outcome for my current issue, including any fees or service credit.")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    q4, q5, q6 = st.columns(3)

    with q4:
        st.markdown(
            """
            <div class="quick-card">
                <div class="quick-icon">🎫</div>
                <div class="quick-title">Investigate Ticket</div>
                <div class="quick-text">
                    Analyze a support ticket and identify the root cause,
                    evidence and recommended resolution.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Investigate Ticket", key="ticket", use_container_width=True):
            set_prompt("Investigate the current support ticket and identify the root cause and recommended resolution.")

    with q5:
        st.markdown(
            """
            <div class="quick-card">
                <div class="quick-icon">👤</div>
                <div class="quick-title">Account Lookup</div>
                <div class="quick-text">
                    Review authenticated account information and
                    relevant customer context.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Account Lookup", key="account", use_container_width=True):
            set_prompt("Review the authenticated account and summarize the relevant customer context.")

    with q6:
        st.markdown(
            """
            <div class="quick-card">
                <div class="quick-icon">✨</div>
                <div class="quick-title">New Investigation</div>
                <div class="quick-text">
                    Start a fresh support investigation with the
                    ParcelPilot AI assistant.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("New Investigation", key="new", use_container_width=True):
            clear_conversation()

    st.markdown("<div style='height:25px'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="section-label">💬 Support Assistant</div>
        <div class="section-sub">
            Ask about an order, account, ticket, policy or operational issue.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="chat-shell">', unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown(
            """
            <div class="empty-chat">
                <div class="empty-icon">🤖</div>
                <div class="empty-title">How can I help?</div>
                <div class="empty-text">
                    Start with one of the quick actions above or describe
                    your customer support issue below. ParcelPilot can
                    retrieve evidence, inspect account context and guide
                    operational decisions.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(
                    f'<div class="message-user">{message["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="message-assistant">{message["content"]}</div>',
                    unsafe_allow_html=True,
                )

    st.markdown("</div>", unsafe_allow_html=True)

    prompt = st.session_state.pending_prompt

    if prompt:
        st.session_state.pending_prompt = None
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        st.rerun()

    user_message = st.chat_input(
        "Ask ParcelPilot AI about an order, policy, ticket or account..."
    )

    if user_message:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        st.rerun()

    st.markdown("<div style='height:25px'></div>", unsafe_allow_html=True)

    a1, a2 = st.columns(2)

    with a1:
        st.markdown(
            """
            <div class="card">
                <div class="card-title">🔐 Security Context</div>
                <div class="card-subtitle">
                    Authorization is derived from the authenticated
                    session rather than user-provided text.
                </div>

                <div class="evidence">
                    <div class="evidence-title">Tenant Isolation</div>
                    <div class="evidence-text">
                        Customer requests remain restricted to the
                        authenticated account context.
                    </div>
                </div>

                <div class="evidence">
                    <div class="evidence-title">Action Protection</div>
                    <div class="evidence-text">
                        State-changing operations can follow
                        preview → confirmation → execution.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with a2:
        st.markdown(
            """
            <div class="card">
                <div class="card-title">🧠 Reliability Layer</div>
                <div class="card-subtitle">
                    Responses are designed around authoritative evidence
                    and deterministic business logic.
                </div>

                <div class="evidence">
                    <div class="evidence-title">Source Precedence</div>
                    <div class="evidence-text">
                        Customer agreement → current policy →
                        product documentation → historical context.
                    </div>
                </div>

                <div class="evidence">
                    <div class="evidence-title">Conflict Detection</div>
                    <div class="evidence-text">
                        Missing verification data or low-confidence
                        retrieval can trigger escalation.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <div class="footer">
        ParcelPilot AI · MCP Agent Architecture · RAG ·
        Evidence-Aware Support · Human-in-the-Loop Actions
    </div>
    """,
    unsafe_allow_html=True,
)
