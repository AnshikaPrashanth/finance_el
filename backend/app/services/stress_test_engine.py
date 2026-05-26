"""
stress_test_engine.py - Stress Testing Module
=============================================
Runs canonical financial stress scenarios and quantifies impact
on key health metrics.
"""

from typing import Dict, List

from app.models.schemas import UserProfile
from app.services.event_engine import EventEngine
from app.services.priority_engine import PriorityEngine
from app.services.state_engine import FinancialState, StateHistory


STRESS_SCENARIOS = [
    {
        "scenario_id": "job_loss_6m",
        "label": "Job Loss (6 months)",
        "event_type": "job_loss",
        "params": {"months": 6},
        "severity": "high",
    },
    {
        "scenario_id": "inflation_spike_5pct",
        "label": "Inflation Spike (+5%)",
        "event_type": "inflation_shock",
        "params": {"delta_pct": 5.0},
        "severity": "medium",
    },
    {
        "scenario_id": "market_crash_40pct",
        "label": "Market Crash (-40%)",
        "event_type": "market_crash",
        "params": {"drawdown_pct": 40.0},
        "severity": "high",
    },
    {
        "scenario_id": "medical_emergency_5l",
        "label": "Medical Emergency (INR 5 Lakh)",
        "event_type": "medical_emergency",
        "params": {"amount": 500_000.0},
        "severity": "medium",
    },
]


SCENARIO_PROBABILITY_BOUNDS = {
    "job_loss_6m": (0.24, 0.55),
    "inflation_spike_5pct": (0.08, 0.24),
    "market_crash_40pct": (0.18, 0.40),
    "medical_emergency_5l": (0.28, 0.60),
}

SCENARIO_RESILIENCE_BOUNDS = {
    "job_loss_6m": (8.0, 18.0),
    "inflation_spike_5pct": (2.0, 7.0),
    "market_crash_40pct": (4.0, 12.0),
    "medical_emergency_5l": (10.0, 22.0),
}


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _blend_linear(value: float, anchors: list[tuple[float, float]]) -> float:
    if value <= anchors[0][0]:
        return anchors[0][1]
    for idx in range(1, len(anchors)):
        left_x, left_y = anchors[idx - 1]
        right_x, right_y = anchors[idx]
        if value <= right_x:
            span = right_x - left_x
            if span <= 0:
                return right_y
            ratio = (value - left_x) / span
            return left_y + ratio * (right_y - left_y)
    return anchors[-1][1]


def _buffer_score(months: float) -> float:
    return _blend_linear(
        months,
        [(0.0, 5), (1.0, 18), (3.0, 45), (6.0, 75), (9.0, 92), (12.0, 100)],
    )


def _liquidity_score(state: FinancialState) -> float:
    liquid_months = (
        (state.liquid_savings + state.emergency_fund + state.debt_portfolio)
        / max(state.monthly_expenses, 1.0)
    )
    return _blend_linear(
        liquid_months,
        [(0.0, 8), (1.0, 22), (3.0, 46), (6.0, 72), (10.0, 92), (14.0, 100)],
    )


def _debt_score(state: FinancialState) -> float:
    high_interest_debt = state.personal_loan + state.credit_card_debt
    debt_pressure = _blend_linear(
        state.debt_to_income_ratio,
        [(0.0, 94), (0.10, 88), (0.20, 74), (0.30, 58), (0.45, 38), (0.60, 18)],
    )
    debt_penalty = _blend_linear(
        high_interest_debt / max(state.monthly_income * 12, 1.0),
        [(0.0, 0), (0.05, 4), (0.10, 8), (0.20, 15), (0.35, 22)],
    )
    return max(0.0, debt_pressure - debt_penalty)


def _surplus_score(state: FinancialState) -> float:
    if state.monthly_income <= 0:
        return 0.0
    surplus_ratio = state.monthly_surplus / state.monthly_income
    return _blend_linear(
        surplus_ratio,
        [(-0.10, 0), (0.0, 18), (0.05, 38), (0.10, 56), (0.20, 78), (0.30, 96)],
    )


def _diversification_score(state: FinancialState) -> float:
    buckets = [
        state.liquid_savings + state.emergency_fund,
        state.equity_portfolio,
        state.debt_portfolio,
        state.epf_ppf,
        state.real_estate,
    ]
    active = sum(1 for value in buckets if value > 0)
    score = _blend_linear(active, [(1, 20), (2, 40), (3, 60), (4, 80), (5, 96)])
    total = max(sum(buckets), 1.0)
    concentration = max(buckets) / total
    penalty = _blend_linear(concentration, [(0.35, 0), (0.50, 3), (0.70, 12), (0.90, 22)])
    return max(0.0, score - penalty)


def _insurance_score(state: FinancialState) -> float:
    if state.monthly_income <= 0:
        return 0.0
    premium_ratio = state.monthly_insurance_premium / state.monthly_income
    if premium_ratio <= 0:
        return 26.0
    return _blend_linear(
        premium_ratio,
        [(0.0, 50), (0.01, 60), (0.03, 72), (0.05, 84), (0.08, 96)],
    )


def _volatility_exposure_score(state: FinancialState) -> float:
    total = max(state.total_assets, 1.0)
    equity_ratio = state.equity_portfolio / total
    return _blend_linear(
        equity_ratio,
        [(0.0, 85), (0.15, 88), (0.30, 82), (0.45, 74), (0.60, 62), (0.80, 46)],
    )


def _scenario_resilience_raw(state: FinancialState) -> float:
    weighted = (
        _buffer_score(state.emergency_fund_months) * 0.23
        + _liquidity_score(state) * 0.17
        + _debt_score(state) * 0.16
        + _surplus_score(state) * 0.15
        + _diversification_score(state) * 0.11
        + _insurance_score(state) * 0.08
        + _volatility_exposure_score(state) * 0.10
    )
    return round(_clamp(weighted, 0.0, 100.0), 1)


def _stress_components(before: FinancialState, after: FinancialState) -> Dict[str, float]:
    baseline_liquidity = before.liquid_savings + before.emergency_fund
    after_liquidity = after.liquid_savings + after.emergency_fund
    baseline_debt = before.personal_loan + before.credit_card_debt + before.home_loan
    after_debt = after.personal_loan + after.credit_card_debt + after.home_loan

    return {
        "liquidity_hit": _clamp(
            (baseline_liquidity - after_liquidity) / max(before.monthly_expenses * 6, 1.0),
            0.0,
            1.0,
        ),
        "return_hit": _clamp(
            (before.expected_return - after.expected_return) / 8.0,
            0.0,
            1.0,
        ),
        "debt_hit": _clamp(
            (after_debt - baseline_debt) / max(before.monthly_income * 12, 1.0),
            0.0,
            1.0,
        ),
        "sip_hit": _clamp(
            (before.monthly_sip - after.monthly_sip) / max(before.monthly_sip, 1.0),
            0.0,
            1.0,
        ),
        "inflation_hit": _clamp(
            (after.inflation_rate - before.inflation_rate) / 6.0,
            0.0,
            1.0,
        ),
        "emergency_hit": _clamp(
            (before.emergency_fund_months - after.emergency_fund_months) / 6.0,
            0.0,
            1.0,
        ),
        "drawdown_hit": _clamp(
            (before.equity_portfolio - after.equity_portfolio) / max(before.total_assets, 1.0),
            0.0,
            1.0,
        ),
        "surplus_hit": _clamp(
            (before.monthly_surplus - after.monthly_surplus) / max(before.monthly_income * 0.20, 1.0),
            0.0,
            1.0,
        ),
    }


def _normalized_probability_after(
    before: FinancialState,
    after: FinancialState,
    scenario_id: str,
    baseline_probability: float,
) -> float:
    components = _stress_components(before, after)
    base_probability = baseline_probability

    severity = (
        components["liquidity_hit"] * 0.22
        + components["return_hit"] * 0.18
        + components["debt_hit"] * 0.15
        + components["sip_hit"] * 0.12
        + components["inflation_hit"] * 0.12
        + components["emergency_hit"] * 0.12
        + components["drawdown_hit"] * 0.05
        + components["surplus_hit"] * 0.04
    )
    severity = _clamp(severity, 0.0, 1.0)

    min_drop, max_drop = SCENARIO_PROBABILITY_BOUNDS.get(scenario_id, (0.10, 0.30))
    raw_probability = min(after.real_success_probability, base_probability + 0.01)

    dampened_drop = min_drop + (max_drop - min_drop) * severity
    dampened_probability = base_probability * (1.0 - dampened_drop)

    normalized = min(raw_probability, dampened_probability, base_probability)
    floor = max(0.0025, base_probability * 0.35 if scenario_id == "inflation_spike_5pct" else base_probability * 0.20)
    return round(_clamp(normalized, floor, base_probability), 4)


def _normalized_resilience_after(
    before: FinancialState, after: FinancialState, scenario_id: str
) -> float:
    components = _stress_components(before, after)
    baseline = _scenario_resilience_raw(before)
    raw_after = _scenario_resilience_raw(after)

    severity = (
        components["liquidity_hit"] * 0.24
        + components["debt_hit"] * 0.18
        + components["emergency_hit"] * 0.16
        + components["surplus_hit"] * 0.16
        + components["drawdown_hit"] * 0.14
        + components["return_hit"] * 0.07
        + components["inflation_hit"] * 0.05
    )
    severity = _clamp(severity, 0.0, 1.0)

    min_reduction, max_reduction = SCENARIO_RESILIENCE_BOUNDS.get(scenario_id, (3.0, 10.0))
    reduction = min_reduction + (max_reduction - min_reduction) * severity

    normalized = min(raw_after, baseline - reduction)
    floor = max(10.0, baseline - (max_reduction + 8.0))
    return round(_clamp(normalized, floor, baseline), 1)


def _recovery_action(before: FinancialState, after: FinancialState) -> str:
    high_interest_debt = after.personal_loan + after.credit_card_debt
    if after.emergency_fund_months < 2.5:
        return "build_emergency_fund"
    if high_interest_debt > 0 and after.debt_to_income_ratio > 0.12:
        return "clear_high_interest_debt"
    if after.monthly_surplus <= before.monthly_surplus * 0.5:
        return "reduce_discretionary_expenses"
    if after.corpus_adequacy_ratio < 0.55 and after.years_to_retirement <= 12:
        return "delay_retirement"
    if after.corpus_adequacy_ratio < 0.75 and after.monthly_surplus > 0:
        return "increase_sip"
    if after.equity_portfolio < after.debt_portfolio and after.years_to_retirement > 12:
        return "rebalance_allocation"
    return "build_emergency_fund"


class StressTestEngine:
    def __init__(self):
        self.priority_engine = PriorityEngine()

    def run_single(
        self,
        state: FinancialState,
        scenario: Dict,
        baseline_probability: float | None = None,
    ) -> Dict:
        engine = EventEngine(StateHistory())
        result = engine.apply(state, scenario["event_type"], scenario["params"])
        after: FinancialState = result["new_state"]

        net_worth_impact = after.net_worth - state.net_worth
        net_worth_base = max(1.0, abs(state.net_worth))
        recovery = _recovery_action(state, after)
        baseline_probability = (
            state.real_success_probability
            if baseline_probability is None
            else baseline_probability
        )
        normalized_probability = _normalized_probability_after(
            state, after, scenario["scenario_id"], baseline_probability
        )
        normalized_resilience = _normalized_resilience_after(state, after, scenario["scenario_id"])

        return {
            "scenario_id": scenario["scenario_id"],
            "label": scenario["label"],
            "severity": scenario["severity"],
            "narrative": result["narrative"],
            "impact": {
                "net_worth_change": round(net_worth_impact, 2),
                "net_worth_change_pct": round((net_worth_impact / net_worth_base) * 100, 2),
                "emergency_fund_months_after": round(after.emergency_fund_months, 2),
                "real_success_probability_after": normalized_probability,
                "real_success_probability_delta": round(
                    normalized_probability - baseline_probability, 4
                ),
                "financial_stress_score_after": round(after.financial_stress_score, 4),
                "financial_stress_delta": round(
                    after.financial_stress_score - state.financial_stress_score, 4
                ),
                "resilience_score_after": normalized_resilience,
            },
            "state_after_summary": {
                "net_worth": round(after.net_worth, 2),
                "emergency_fund": round(after.emergency_fund, 2),
                "equity_portfolio": round(after.equity_portfolio, 2),
                "is_employed": after.is_employed,
            },
            "recommended_recovery_action": recovery,
            "recovery_rationale": _recovery_rationale(recovery),
            "ranked_recovery_actions": self.priority_engine.rank_actions(after, top_n=3),
        }

    def run_all(
        self,
        state: FinancialState,
        scenario_ids: List[str] | None = None,
        baseline_probability: float | None = None,
    ) -> Dict:
        scenarios = STRESS_SCENARIOS
        if scenario_ids:
            scenarios = [item for item in STRESS_SCENARIOS if item["scenario_id"] in scenario_ids]

        baseline_probability = (
            state.real_success_probability
            if baseline_probability is None
            else baseline_probability
        )
        results = [
            self.run_single(state, scenario, baseline_probability=baseline_probability)
            for scenario in scenarios
        ]
        worst = min(results, key=lambda item: item["impact"]["resilience_score_after"])
        resilience_score = round(
            sum(item["impact"]["resilience_score_after"] for item in results) / len(results),
            1,
        )

        return {
            "baseline": {
                "net_worth": round(state.net_worth, 2),
                "emergency_fund_months": round(state.emergency_fund_months, 2),
                "real_success_probability": round(baseline_probability, 4),
                "financial_stress_score": round(state.financial_stress_score, 4),
                "resilience_score": _scenario_resilience_raw(state),
            },
            "scenarios": results,
            "summary": {
                "worst_case_scenario": worst["label"],
                "worst_case_rsp_drop": round(
                    worst["impact"]["real_success_probability_delta"], 4
                ),
                "resilience_score": resilience_score,
                "overall_risk_level": _risk_level(resilience_score),
            },
        }


def build_state_from_profile(profile: UserProfile, user_id: str = "default") -> FinancialState:
    monthly_income = (
        profile.income.monthly_salary
        + profile.income.side_income
        + profile.income.rental_income
        + profile.income.other_income
        + (profile.income.bonus / 12)
    )
    monthly_expenses = (
        profile.expenses.living_expenses
        + profile.expenses.discretionary_spending
        + profile.expenses.insurance
        + profile.expenses.education_expenses
        + profile.expenses.other_expenses
    )
    target_corpus = profile.investments.target_corpus
    if target_corpus <= 0:
        target_corpus = monthly_expenses * 12 * 25
    return FinancialState(
        user_id=user_id,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        monthly_sip=profile.investments.sip_amount,
        monthly_emi=profile.expenses.emi_payments,
        liquid_savings=profile.assets.savings,
        equity_portfolio=profile.assets.stocks + profile.assets.mutual_funds,
        debt_portfolio=profile.assets.fixed_deposits + profile.assets.nps + profile.assets.gold,
        real_estate=profile.assets.real_estate,
        epf_ppf=profile.assets.epf + profile.assets.ppf,
        emergency_fund=profile.assets.emergency_fund,
        monthly_insurance_premium=profile.expenses.insurance,
        home_loan=profile.liabilities.home_loan,
        personal_loan=profile.liabilities.personal_loan,
        credit_card_debt=profile.liabilities.credit_card_debt,
        target_corpus=target_corpus,
        current_age=profile.personal.age,
        retirement_age=profile.personal.retirement_age,
        dependents=profile.personal.dependents,
        risk_appetite=profile.investments.risk_appetite.lower(),
        expected_return=profile.investments.expected_annual_return,
        inflation_rate=profile.investments.inflation_rate,
    )


def _recovery_rationale(action: str) -> str:
    rationales = {
        "build_emergency_fund": (
            "Liquidity took the biggest hit here. Rebuilding a 6-month emergency cushion will "
            "restore flexibility before you push harder on growth."
        ),
        "clear_high_interest_debt": (
            "Expensive debt is now putting visible pressure on monthly cash flow. Reducing it "
            "should improve resilience faster than most alternatives."
        ),
        "increase_sip": (
            "The long-term goal has slipped, but your cash flow can still support a measured "
            "increase in investing."
        ),
        "reduce_discretionary_expenses": (
            "This shock mainly tightens monthly flexibility, so trimming optional expenses is "
            "the quickest stabilizer."
        ),
        "delay_retirement": (
            "A slightly longer accumulation window can offset the stress impact without requiring "
            "an unrealistic jump in monthly savings."
        ),
        "rebalance_allocation": (
            "Your recovery can benefit from a more growth-oriented mix, provided it fits your "
            "risk comfort and time horizon."
        ),
    }
    return rationales.get(action, "Review the plan and rebalance priorities gradually.")


def _risk_level(resilience_score: float) -> str:
    if resilience_score >= 70:
        return "LOW"
    if resilience_score >= 45:
        return "MEDIUM"
    return "HIGH"
