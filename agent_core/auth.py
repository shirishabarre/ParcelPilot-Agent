"""
Mock authentication. In a real deployment this would validate a JWT/session
cookie against an identity provider; here it's a small lookup so the demo
can show scoping cleanly. The important part: the orchestrator reads
caller_role/caller_account_id from THIS module and injects them into every
tool call — it never trusts the LLM or the user's free-text message for
scoping.
"""
from dataclasses import dataclass

# demo users — in real life this is a DB/IdP lookup
_USERS = {
    "northstar_user": {"role": "customer", "account_id": "ACCT-001", "display_name": "Northstar Logistics user"},
    "lumenworks_user": {"role": "customer", "account_id": "ACCT-002", "display_name": "LumenWorks user"},
    "beacon_user": {"role": "customer", "account_id": "ACCT-003", "display_name": "Beacon Retail user"},
    "rohit": {"role": "staff", "account_id": None, "display_name": "Rohit (Support)"},
    "maya": {"role": "staff", "account_id": None, "display_name": "Maya (Support)"},
}


@dataclass
class Session:
    user_id: str
    role: str            # "customer" | "staff"
    account_id: str | None  # required if role == customer; None for staff (all-account access)
    display_name: str


def login(user_id: str) -> Session:
    if user_id not in _USERS:
        raise ValueError(f"Unknown user_id '{user_id}' (mock auth — see agent_core/auth.py _USERS)")
    u = _USERS[user_id]
    return Session(user_id=user_id, role=u["role"], account_id=u["account_id"], display_name=u["display_name"])


def list_demo_users() -> list[str]:
    return list(_USERS.keys())
