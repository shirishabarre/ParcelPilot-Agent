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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html,body,[class*="css"]{
    font-family:'Inter',sans-serif;
}

.stApp{
    background:
        radial-gradient(circle at 10% 0%,rgba(37,99,235,.14),transparent 28%),
        radial-gradient(circle at 90% 5%,rgba(14,165,233,.09),transparent 25%),
        #060a12;
    color:#f8fafc;
}

.block-container{
    max-width:1450px;
    padding-top:1.4rem;
    padding-bottom:3rem;
}

#MainMenu,footer{
    visibility:hidden;
}

header{
    background:transparent!important;
}

section[data-testid="stSidebar"]{
    background:#070b13;
    border-right:1px solid rgba(148,163,184,.08);
}

.brand{
    display:flex;
    align-items:center;
    gap:12px;
    padding:8px 4px 25px;
}

.brand-icon{
    width:44px;
    height:44px;
    border-radius:13px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:linear-gradient(135deg,#2563eb,#06b6d4);
    box-shadow:0 12px 30px rgba(37,99,235,.28);
    font-size:22px;
}

.brand-title{
    font-size:18px;
    font-weight:800;
    color:#f8fafc;
}

.brand-subtitle{
    color:#475569;
    font-size:9px;
    font-weight:700;
    letter-spacing:1.2px;
    margin-top:2px;
}

.sidebar-title{
    color:#475569;
    font-size:9px;
    font-weight:800;
    letter-spacing:1.2px;
    text-transform:uppercase;
    margin:17px 3px 8px;
}

.sidebar-status{
    display:flex;
    align-items:center;
    gap:7px;
    padding:8px 10px;
    margin:5px 0;
    border-radius:9px;
    background:rgba(15,23,42,.65);
    border:1px solid rgba(148,163,184,.07);
    color:#94a3b8;
    font-size:10px;
}

.status-dot{
    width:6px;
    height:6px;
    border-radius:50%;
    background:#22c55e;
    box-shadow:0 0 8px rgba(34,197,94,.65);
}

.session-card{
    margin-top:18px;
    padding:13px;
    border-radius:13px;
    background:rgba(15,23,42,.65);
    border:1px solid rgba(148,163,184,.08);
}

.session-row{
    display:flex;
    justify-content:space-between;
    gap:10px;
    margin:7px 0;
}

.session-key{
    color:#475569;
    font-size:9px;
}

.session-value{
    color:#cbd5e1;
    font-size:9px;
    font-weight:700;
    text-align:right;
}

.online{
    display:inline-flex;
    align-items:center;
    gap:6px;
    padding:5px 8px;
    border-radius:999px;
    color:#86efac;
    background:rgba(34,197,94,.07);
    border:1px solid rgba(34,197,94,.14);
    font-size:8px;
    font-weight:800;
}

.hero{
    padding:8px 0 20px;
}

.eyebrow{
    color:#60a5fa;
    font-size:9px;
    font-weight:800;
    letter-spacing:1.8px;
    margin-bottom:8px;
}

.hero-title{
    font-size:38px;
    line-height:1.08;
    letter-spacing:-1.8px;
    font-weight:800;
    color:#f8fafc;
}

.hero-title span{
    background:linear-gradient(90deg,#60a5fa,#22d3ee);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

.hero-description{
    color:#64748b;
    max-width:720px;
    font-size:12px;
    line-height:1.7;
    margin-top:9px;
}

.metric{
    padding:16px;
    min-height:95px;
    border-radius:15px;
    background:linear-gradient(145deg,rgba(15,23,42,.88),rgba(8,13,23,.82));
    border:1px solid rgba(148,163,184,.08);
}

.metric-label{
    color:#475569;
    font-size:8px;
    font-weight:800;
    letter-spacing:1px;
    text-transform:uppercase;
}

.metric-value{
    color:#f8fafc;
    font-size:19px;
    font-weight:800;
    margin-top:7px;
}

.metric-description{
    color:#64748b;
    font-size:8px;
    margin-top:3px;
}

.section-title{
    color:#f8fafc;
    font-size:15px;
    font-weight:750;
}

.section-description{
    color:#64748b;
    font-size:10px;
    margin-top:3px;
    margin-bottom:12px;
}

.action-card{
    min-height:145px;
    padding:17px;
    border-radius:16px;
    background:linear-gradient(145deg,rgba(15,23,42,.9),rgba(8,13,23,.78));
    border:1px solid rgba(148,163,184,.08);
}

.action-icon{
    font-size:24px;
    margin-bottom:8px;
}

.action-title{
    color:#f8fafc;
    font-size:12px;
    font-weight:750;
}

.action-description{
    color:#64748b;
    font-size:9px;
    line-height:1.55;
    margin-top:5px;
}

.login-card{
    padding:24px;
    border-radius:18px;
    background:linear-gradient(145deg,rgba(15,23,42,.95),rgba(7,12,22,.94));
    border:1px solid rgba(96,165,250,.13);
    box-shadow:0 25px 70px rgba(0,0,0,.25);
}

.login-title{
    color:#f8fafc;
    font-size:19px;
    font-weight:800;
}

.login-description{
    color:#64748b;
    font-size:10px;
    line-height:1.6;
    margin-top:5px;
    margin-bottom:17px;
}

.footer{
    text-align:center;
    color:#334155;
    font-size:8px;
    margin-top:42px;
    padding-top:18px;
    border-top:1px solid rgba(148,163,184,.05);
}

div[data-testid="stButton"]>button{
    min-height:39px;
    border-radius:10px;
    border:1px solid rgba(96,165,250,.16);
    background:linear-gradient(135deg,#2563eb,#1d4ed8);
    color:white;
    font-size:10px;
    font-weight:750;
}

div[data-testid="stButton"]>button:hover{
    border-color:rgba(147,197,253,.35);
    box-shadow:0 8px 25px rgba(37,99,235,.2);
}

div[data-testid="stButton"]>button[kind="secondary"]{
    background:rgba(15,23,42,.7);
    border-color:rgba(148,163,184,.1);
    color:#cbd5e1;
    box-shadow:none;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"]{
    background:#0b1220!important;
    border-color:rgba(148,163,184,.1)!important;
    border-radius:10px!important;
}

.stAlert{
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

if "session" not in st.session_state:
    st.session_state.session = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = None


def clear_chat():
    st.session_state.messages = []
    st.session_state.quick_prompt = None
    st.rerun()


def logout():
    st.session_state.session = None
    st.session_state.messages = []
    st.session_state.quick_prompt = None
    st.rerun()


def quick_action(prompt):
    st.session_state.quick_prompt = prompt
    st.switch_page("pages/1_Customer_Support_Chat.py")


with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div class="brand-icon">📦</div>
        <div>
            <div class="brand-title">ParcelPilot</div>
            <div class="brand-subtitle">AI SUPPORT INTELLIGENCE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="sidebar-title">Workspace</div>',
        unsafe_allow_html=True,
    )

    if st.button("💬  Support Assistant", use_container_width=True):
        st.switch_page("pages/1_Customer_Support_Chat.py")

    st.markdown(
        '<div class="sidebar-title">System</div>',
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div class="sidebar-status">
        <span class="status-dot"></span>
        Agent Online
    </div>
    <div class="sidebar-status">
        <span class="status-dot"></span>
        RAG Available
    </div>
    <div class="sidebar-status">
        <span class="status-dot"></span>
        MCP Tools Ready
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.session:
        s = st.session_state.session

        role = "Customer" if s.role == "customer" else "Internal Support"
        account = s.account_id if s.account_id else "All Accounts"

        st.markdown(
            f"""
            <div class="session-card">
                <div class="session-row">
                    <span class="session-key">User</span>
                    <span class="session-value">{s.display_name}</span>
                </div>
                <div class="session-row">
                    <span class="session-key">Role</span>
                    <span class="session-value">{role}</span>
                </div>
                <div class="session-row">
                    <span class="session-key">Account</span>
                    <span class="session-value">{account}</span>
                </div>
                <div style="margin-top:10px">
                    <span class="online">
                        <span class="status-dot"></span>
                        Secure session
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:9px'></div>", unsafe_allow_html=True)

        if st.button("🧹  Clear Chat", use_container_width=True, type="secondary"):
            clear_chat()

        if st.button("↪  Sign Out", use_container_width=True, type="secondary"):
            logout()


st.markdown("""
<div class="hero">
    <div class="eyebrow">PARCELPILOT AI</div>
    <div class="hero-title">
        Intelligent support.<br>
        <span>Built for reliable decisions.</span>
    </div>
    <div class="hero-description">
        Investigate customer issues, retrieve authoritative information,
        work with operational data and safely handle support requests
        through one AI workspace.
    </div>
</div>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)

metrics = [
    ("Agent", "Online", "Ready for requests"),
    ("Knowledge", "RAG", "Evidence retrieval"),
    ("Tools", "3+", "Operational capabilities"),
    ("Actions", "HITL", "Confirmation protected"),
]

for column, (label, value, description) in zip(
    [m1, m2, m3, m4],
    metrics,
):
    with column:
        st.markdown(
            f"""
            <div class="metric">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-description">{description}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='height:25px'></div>", unsafe_allow_html=True)

if not st.session_state.session:

    left, right = st.columns([1.3, 1], gap="large")

    with left:
        st.markdown("""
        <div class="action-card" style="min-height:310px">
            <div class="action-icon">🤖</div>
            <div class="action-title" style="font-size:18px">
                ParcelPilot Support Assistant
            </div>
            <div class="action-description" style="font-size:11px;max-width:650px">
                A focused AI workspace for answering support questions,
                investigating orders and tickets, retrieving policies and
                working with customer-specific operational information.
            </div>

            <div style="height:22px"></div>

            <div class="action-title">Core capabilities</div>

            <div style="height:10px"></div>

            <div class="action-description" style="font-size:10px">
                🔎 Document and policy retrieval
            </div>
            <div class="action-description" style="font-size:10px">
                📊 Account, order and ticket lookup
            </div>
            <div class="action-description" style="font-size:10px">
                🧮 Deterministic business calculations
            </div>
            <div class="action-description" style="font-size:10px">
                🔐 Account-aware access control
            </div>
            <div class="action-description" style="font-size:10px">
                🤝 Human confirmation for protected actions
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="login-card">
            <div class="login-title">🔐 Enter Workspace</div>
            <div class="login-description">
                Choose a demo identity to authenticate into ParcelPilot.
            </div>
        """, unsafe_allow_html=True)

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

        st.markdown("</div>", unsafe_allow_html=True)

else:

    s = st.session_state.session

    role = "Customer" if s.role == "customer" else "Internal Support"
    account = s.account_id if s.account_id else "All Accounts"

    st.markdown(
        f"""
        <div class="action-card">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <div>
                    <div class="action-title" style="font-size:16px">
                        Welcome back, {s.display_name}
                    </div>
                    <div class="action-description">
                        {role} · {account}
                    </div>
                </div>
                <span class="online">
                    <span class="status-dot"></span>
                    Authenticated
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">Quick Actions</div>'
        '<div class="section-description">'
        'Start a common support workflow.'
        '</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="action-card">
            <div class="action-icon">📦</div>
            <div class="action-title">Track an Order</div>
            <div class="action-description">
                Investigate order status and delivery information.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Track Order", key="track", use_container_width=True):
            quick_action("Please investigate the current status of my order.")

    with c2:
        st.markdown("""
        <div class="action-card">
            <div class="action-icon">📄</div>
            <div class="action-title">Check a Policy</div>
            <div class="action-description">
                Find the applicable policy or customer agreement.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Check Policy", key="policy", use_container_width=True):
            quick_action("Please find the applicable policy for my issue.")

    with c3:
        st.markdown("""
        <div class="action-card">
            <div class="action-icon">🧮</div>
            <div class="action-title">Calculate Outcome</div>
            <div class="action-description">
                Determine the applicable fee, credit or outcome.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Calculate Outcome", key="calculate", use_container_width=True):
            quick_action("Please calculate the applicable outcome for my issue.")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3)

    with c4:
        st.markdown("""
        <div class="action-card">
            <div class="action-icon">🎫</div>
            <div class="action-title">Investigate Ticket</div>
            <div class="action-description">
                Analyze a support ticket and determine the next step.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Investigate Ticket", key="ticket", use_container_width=True):
            quick_action("Please investigate the relevant support ticket and identify the likely issue.")

    with c5:
        st.markdown("""
        <div class="action-card">
            <div class="action-icon">👤</div>
            <div class="action-title">Account Lookup</div>
            <div class="action-description">
                Review the authenticated account context.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Account Lookup", key="account", use_container_width=True):
            quick_action("Please retrieve the relevant information for my authenticated account.")

    with c6:
        st.markdown("""
        <div class="action-card">
            <div class="action-icon">✨</div>
            <div class="action-title">Open Assistant</div>
            <div class="action-description">
                Continue directly to the support conversation.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Open Chat", key="chat", use_container_width=True):
            st.switch_page("pages/1_Customer_Support_Chat.py")

st.markdown(
    """
    <div class="footer">
        ParcelPilot AI · Customer Support Intelligence
    </div>
    """,
    unsafe_allow_html=True,
)
