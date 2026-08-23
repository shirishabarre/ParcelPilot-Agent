"""
Data access layer over ParcelPilot_Assessment_Data.xlsx.

Access control lives HERE, not in the LLM prompt: every read that returns
customer data takes (caller_role, caller_account_id) and a customer caller
is hard-filtered to their own account_id before any row is returned. This
satisfies "access controls enforced in the data/tool layer" even if the
model is jailbroken or mistaken about scope.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
XLSX_PATH = ROOT / "data" / "raw" / "ParcelPilot_Assessment_Data.xlsx"


class AccessDeniedError(Exception):
    pass


class Repository:
    def __init__(self, xlsx_path: Path = XLSX_PATH):
        self.accounts = pd.read_excel(xlsx_path, sheet_name="accounts")
        self.orders = pd.read_excel(xlsx_path, sheet_name="orders")
        self.tickets = pd.read_excel(xlsx_path, sheet_name="tickets")

    # ---- access-control guard -------------------------------------------------
    @staticmethod
    def _check_scope(caller_role: str, caller_account_id: str | None, target_account_id: str):
        if caller_role == "staff":
            return  # authorised internal users may access any account
        if caller_role == "customer":
            if not caller_account_id or caller_account_id != target_account_id:
                raise AccessDeniedError(
                    f"Customer session for '{caller_account_id}' may not access data for '{target_account_id}'."
                )
            return
        raise AccessDeniedError(f"Unknown role '{caller_role}'.")

    # ---- accounts ---------------------------------------------------------
    def get_account(self, account_id: str, caller_role: str, caller_account_id: str | None) -> dict:
        self._check_scope(caller_role, caller_account_id, account_id)
        row = self.accounts[self.accounts.account_id == account_id]
        if row.empty:
            return {"error": f"No such account: {account_id}"}
        return row.iloc[0].where(pd.notnull(row.iloc[0]), None).to_dict()

    # ---- orders -------------------------------------------------------------
    def get_order(self, order_id: str, caller_role: str, caller_account_id: str | None) -> dict:
        row = self.orders[self.orders.order_id == order_id]
        if row.empty:
            return {"error": f"No such order: {order_id}"}
        order = row.iloc[0].where(pd.notnull(row.iloc[0]), None).to_dict()
        self._check_scope(caller_role, caller_account_id, order["account_id"])
        return order

    def list_orders(self, account_id: str, caller_role: str, caller_account_id: str | None) -> list[dict]:
        self._check_scope(caller_role, caller_account_id, account_id)
        rows = self.orders[self.orders.account_id == account_id]
        return rows.where(pd.notnull(rows), None).to_dict(orient="records")

    # ---- tickets ------------------------------------------------------------
    def list_tickets(self, account_id: str, caller_role: str, caller_account_id: str | None,
                      status: str | None = None) -> list[dict]:
        self._check_scope(caller_role, caller_account_id, account_id)
        rows = self.tickets[self.tickets.account_id == account_id]
        if status:
            rows = rows[rows.status == status]
        return rows.where(pd.notnull(rows), None).to_dict(orient="records")

    def list_all_tickets_for_staff(self, caller_role: str) -> list[dict]:
        # Used only by internal analytics (Problem 1) — staff-only, never exposed to customer role.
        if caller_role != "staff":
            raise AccessDeniedError("Only staff may list tickets across all accounts.")
        return self.tickets.where(pd.notnull(self.tickets), None).to_dict(orient="records")

    def list_all_orders_for_staff(self, caller_role: str) -> list[dict]:
        if caller_role != "staff":
            raise AccessDeniedError("Only staff may list orders across all accounts.")
        return self.orders.where(pd.notnull(self.orders), None).to_dict(orient="records")
