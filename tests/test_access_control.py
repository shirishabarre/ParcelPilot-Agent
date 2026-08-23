import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp_servers" / "data_server"))
from repository import AccessDeniedError, Repository  # noqa: E402

repo = Repository()


def test_customer_can_access_own_account():
    acc = repo.get_account("ACCT-001", caller_role="customer", caller_account_id="ACCT-001")
    assert acc["account_id"] == "ACCT-001"


def test_customer_cannot_access_other_account():
    with pytest.raises(AccessDeniedError):
        repo.get_account("ACCT-002", caller_role="customer", caller_account_id="ACCT-001")


def test_customer_cannot_list_other_accounts_orders():
    with pytest.raises(AccessDeniedError):
        repo.list_orders("ACCT-002", caller_role="customer", caller_account_id="ACCT-001")


def test_customer_cannot_fetch_order_belonging_to_other_account():
    # ORD-2001 belongs to ACCT-002 (LumenWorks); a Northstar (ACCT-001) customer must not read it
    with pytest.raises(AccessDeniedError):
        repo.get_order("ORD-2001", caller_role="customer", caller_account_id="ACCT-001")


def test_staff_can_access_any_account():
    acc = repo.get_account("ACCT-002", caller_role="staff", caller_account_id=None)
    assert acc["account_id"] == "ACCT-002"


def test_customer_cannot_list_all_tickets():
    with pytest.raises(AccessDeniedError):
        repo.list_all_tickets_for_staff(caller_role="customer")


def test_unknown_role_denied():
    with pytest.raises(AccessDeniedError):
        repo.get_account("ACCT-001", caller_role="bogus_role", caller_account_id="ACCT-001")
