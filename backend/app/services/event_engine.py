"""
event_engine.py - Event-Driven State Evolution
==============================================
Implements discrete financial events that mutate the FinancialState.
Each event is a pure function: (state, params) -> new_state.
Events are composable and reversible via state cloning before application.

Event taxonomy:
  INCOME EVENTS   : salary_increase, job_loss
  MACRO EVENTS    : inflation_shock, market_crash
  EXPENSE EVENTS  : medical_emergency, expense_increase
  LIABILITY EVENTS: emi_closure
  INVESTMENT EVTS : sip_increase
"""

from datetime import datetime
from typing import Any, Callable, Dict, Tuple

from app.services.state_engine import FinancialState, StateHistory


EVENT_REGISTRY: Dict[str, Callable[..., Tuple[FinancialState, str]]] = {}


def register_event(name: str) -> Callable:
    def decorator(fn: Callable) -> Callable:
        EVENT_REGISTRY[name] = fn
        return fn

    return decorator


@register_event("salary_increase")
def salary_increase(
    state: FinancialState, params: Dict[str, Any]
) -> Tuple[FinancialState, str]:
    s = state.clone()
    pct = float(params.get("pct", 10.0))
    delta = s.monthly_income * (pct / 100)
    s.monthly_income += delta
    return (
        s,
        f"Salary increased by {pct}% (+INR {delta:,.0f}/mo). "
        f"New income: INR {s.monthly_income:,.0f}/mo.",
    )


@register_event("job_loss")
def job_loss(state: FinancialState, params: Dict[str, Any]) -> Tuple[FinancialState, str]:
    s = state.clone()
    months = int(params.get("months", 3))
    s.is_employed = False
    s.months_of_job_loss = months

    total_burn = s.monthly_expenses * months
    ef_draw = min(s.emergency_fund, total_burn)
    s.emergency_fund -= ef_draw

    remaining = total_burn - ef_draw
    liquid_draw = min(s.liquid_savings, remaining)
    s.liquid_savings -= liquid_draw
    s.monthly_sip = 0.0

    return (
        s,
        f"Job loss simulated for {months} months. Emergency fund drained by "
        f"INR {ef_draw:,.0f}. Liquid savings reduced by INR {liquid_draw:,.0f}. "
        "SIP paused.",
    )


@register_event("inflation_shock")
def inflation_shock(
    state: FinancialState, params: Dict[str, Any]
) -> Tuple[FinancialState, str]:
    s = state.clone()
    delta = float(params.get("delta_pct", 3.0))
    expense_hike = s.monthly_expenses * (delta / 100)
    s.monthly_expenses += expense_hike
    s.inflation_rate += delta

    return (
        s,
        f"Inflation shock of +{delta}%. Monthly expenses up by INR {expense_hike:,.0f}. "
        f"New inflation rate: {s.inflation_rate:.1f}%.",
    )


@register_event("medical_emergency")
def medical_emergency(
    state: FinancialState, params: Dict[str, Any]
) -> Tuple[FinancialState, str]:
    s = state.clone()
    amount = float(params.get("amount", 200_000.0))

    ef_draw = min(s.emergency_fund, amount)
    s.emergency_fund -= ef_draw
    remaining = amount - ef_draw

    liquid_draw = min(s.liquid_savings, remaining)
    s.liquid_savings -= liquid_draw
    remaining -= liquid_draw

    if remaining > 0:
        s.personal_loan += remaining
        s.monthly_emi += remaining / 24

    return (
        s,
        f"Medical emergency of INR {amount:,.0f}. EF used: INR {ef_draw:,.0f}, "
        f"liquid savings used: INR {liquid_draw:,.0f}, new debt: INR {remaining:,.0f}.",
    )


@register_event("emi_closure")
def emi_closure(state: FinancialState, params: Dict[str, Any]) -> Tuple[FinancialState, str]:
    s = state.clone()
    loan_type = str(params.get("loan_type", "personal_loan"))
    old_principal = float(getattr(s, loan_type, 0.0))

    if loan_type not in {"personal_loan", "credit_card_debt", "home_loan"}:
        return s, f"Unknown loan type: {loan_type}"

    emi_freed = s.monthly_emi * (old_principal / max(1.0, s.total_liabilities))
    setattr(s, loan_type, 0.0)
    s.monthly_emi = max(0.0, s.monthly_emi - emi_freed)

    return (
        s,
        f"{loan_type.replace('_', ' ').title()} closed. Principal cleared: "
        f"INR {old_principal:,.0f}. EMI freed: INR {emi_freed:,.0f}/mo.",
    )


@register_event("sip_increase")
def sip_increase(
    state: FinancialState, params: Dict[str, Any]
) -> Tuple[FinancialState, str]:
    s = state.clone()
    if "amount" in params:
        delta = float(params["amount"])
    else:
        pct = float(params.get("pct", 10.0))
        delta = s.monthly_sip * (pct / 100)

    s.monthly_sip += delta
    return s, f"SIP increased by INR {delta:,.0f}/mo. New SIP: INR {s.monthly_sip:,.0f}/mo."


@register_event("expense_increase")
def expense_increase(
    state: FinancialState, params: Dict[str, Any]
) -> Tuple[FinancialState, str]:
    s = state.clone()
    if "amount" in params:
        delta = float(params["amount"])
    else:
        pct = float(params.get("pct", 10.0))
        delta = s.monthly_expenses * (pct / 100)

    s.monthly_expenses += delta
    return (
        s,
        f"Monthly expenses increased by INR {delta:,.0f}. "
        f"New expenses: INR {s.monthly_expenses:,.0f}/mo.",
    )


@register_event("market_crash")
def market_crash(
    state: FinancialState, params: Dict[str, Any]
) -> Tuple[FinancialState, str]:
    s = state.clone()
    drawdown = float(params.get("drawdown_pct", 30.0))
    loss = s.equity_portfolio * (drawdown / 100)
    s.equity_portfolio = max(0.0, s.equity_portfolio - loss)
    s.expected_return = max(4.0, s.expected_return - drawdown * 0.2)

    return (
        s,
        f"Market crash of -{drawdown}%. Equity portfolio lost INR {loss:,.0f}. "
        f"Expected return reduced to {s.expected_return:.1f}%.",
    )


class EventEngine:
    def __init__(self, history: StateHistory | None = None):
        self.history = history or StateHistory()

    def apply(
        self, state: FinancialState, event_type: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        if event_type not in EVENT_REGISTRY:
            raise ValueError(
                f"Unknown event type: '{event_type}'. Valid events: {list(EVENT_REGISTRY.keys())}"
            )

        self.history.record(state, f"before_{event_type}")
        handler = EVENT_REGISTRY[event_type]
        new_state, narrative = handler(state, params)
        self.history.record(new_state, event_type)

        diff = self.history.diff()
        return {
            "event_type": event_type,
            "params": params,
            "narrative": narrative,
            "timestamp": datetime.utcnow().isoformat(),
            "state_before": self.history.snapshots[-2],
            "state_after": new_state.to_dict(),
            "delta": {
                "net_worth": diff.get("net_worth", 0),
                "real_success_probability": diff.get("real_success_probability", 0),
                "financial_stress_score": diff.get("financial_stress_score", 0),
                "emergency_fund_months": diff.get("emergency_fund_months", 0),
                "corpus_adequacy_ratio": diff.get("corpus_adequacy_ratio", 0),
            },
            "new_state": new_state,
        }

    def available_events(self) -> list[str]:
        return list(EVENT_REGISTRY.keys())
