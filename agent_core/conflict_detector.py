"""
Trust & reliability layer (client Problem 2).

Rather than trusting the LLM to "know" when it's unsure, this module gives
the orchestrator explicit, checkable signals to decide whether to answer
directly or escalate to a human:

  1. Deprecated-source guard: fail loudly if a deprecated doc ever appears
     in retrieval results (defense in depth — retriever already excludes it).
  2. Low-confidence retrieval: best doc match score below a floor -> treat
     as "no reliable source found".
  3. needs_verification flags returned by calculators (missing carrier_fault,
     missing timestamps, etc.) -> never let the model paper over these.
  4. Historical-ticket-only support: if the only support for a claim is a
     historical ticket's `historical_resolution` field, downgrade confidence
     — those may be wrong per the task brief.
  5. Manager-approval threshold on service credits -> action requires an
     extra explicit note in the escalation preview, not silent auto-approval.
"""
from dataclasses import dataclass, field

MIN_RELEVANCE_SCORE = 0.8  # BM25-with-authority-weight score floor for "reliable" doc evidence


@dataclass
class ReliabilityCheck:
    ok: bool
    reasons: list[str] = field(default_factory=list)
    should_escalate: bool = False


def check_doc_results(doc_results: list[dict]) -> ReliabilityCheck:
    reasons = []
    for r in doc_results:
        if r.get("status") == "DEPRECATED":
            # Should never happen (excluded at index time) — treat as a hard stop if it ever does.
            return ReliabilityCheck(ok=False, reasons=["A deprecated source was returned — refusing to use it."],
                                     should_escalate=True)
    if not doc_results:
        return ReliabilityCheck(ok=False, reasons=["No matching policy/contract/product-doc text found."],
                                 should_escalate=True)
    if doc_results[0].get("relevance_score", 0) < MIN_RELEVANCE_SCORE:
        reasons.append(f"Best document match score ({doc_results[0].get('relevance_score')}) is low — "
                        f"treat the retrieved text as weak support, verify or escalate.")
        return ReliabilityCheck(ok=False, reasons=reasons, should_escalate=True)
    return ReliabilityCheck(ok=True)


def check_calculation_result(calc_result: dict) -> ReliabilityCheck:
    if calc_result.get("needs_verification"):
        return ReliabilityCheck(ok=False, reasons=[calc_result.get("reason", "Calculation needs verification.")],
                                 should_escalate=True)
    if calc_result.get("needs_manager_approval"):
        return ReliabilityCheck(ok=True,
                                 reasons=["Amount exceeds manager-approval threshold — flag in any escalation/action."],
                                 should_escalate=False)
    return ReliabilityCheck(ok=True)


def check_historical_ticket_reliance(used_only_historical_ticket: bool) -> ReliabilityCheck:
    if used_only_historical_ticket:
        return ReliabilityCheck(
            ok=False,
            reasons=["The only support found was a past ticket's resolution note, which may be incorrect. "
                     "Do not present it as current policy — verify against current policy/SOP/contract or escalate."],
            should_escalate=True,
        )
    return ReliabilityCheck(ok=True)
