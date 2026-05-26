"""
priority_engine.py - Next-Best-Action Priority Engine
=====================================================
Ranks candidate financial actions by their marginal improvement
across multiple outcome dimensions.
"""

from typing import Dict, List

from app.services.state_engine import FinancialState


ACTIONS = [
    "build_emergency_fund",
    "clear_high_interest_debt",
    "increase_sip",
    "reduce_discretionary_expenses",
    "rebalance_allocation",
    "delay_retirement",
]


WEIGHT_PROFILES = {
    "conservative": [0.15, 0.35, 0.25, 0.15, 0.10],
    "moderate": [0.25, 0.25, 0.20, 0.20, 0.10],
    "aggressive": [0.35, 0.10, 0.15, 0.30, 0.10],
}


def _action_context_bonus(state: FinancialState, action: str) -> float:
    high_interest_debt = state.personal_loan + state.credit_card_debt

    if action == "build_emergency_fund":
        if state.emergency_fund_months < 2:
            return 0.22
        if state.emergency_fund_months < 4:
            return 0.10
        return -0.02

    if action == "clear_high_interest_debt":
        if state.credit_card_debt > 0:
            return 0.18
        if high_interest_debt > 0 and state.debt_to_income_ratio > 0.18:
            return 0.10
        return -0.08

    if action == "increase_sip":
        if state.monthly_surplus > max(5_000, state.monthly_income * 0.10) and state.corpus_adequacy_ratio < 0.80:
            return 0.12
        return -0.02

    if action == "reduce_discretionary_expenses":
        if state.monthly_surplus < state.monthly_income * 0.05:
            return 0.10
        return 0.0

    if action == "rebalance_allocation":
        if state.equity_portfolio < state.debt_portfolio and state.years_to_retirement > 10:
            return 0.08
        return -0.01

    if action == "delay_retirement":
        if state.corpus_adequacy_ratio < 0.60 and state.years_to_retirement <= 15:
            return 0.12
        return 0.0

    return 0.0


def _simulate_action(state: FinancialState, action: str) -> FinancialState:
    s = state.clone()
    surplus = state.monthly_surplus
    expenses = state.monthly_expenses

    if action == "build_emergency_fund":
        contribution = surplus * 0.5
        s.emergency_fund += contribution
        s.liquid_savings = max(0.0, s.liquid_savings - contribution)

    elif action == "clear_high_interest_debt":
        payment = surplus * 0.7
        if s.credit_card_debt > 0:
            paid = min(s.credit_card_debt, payment)
            s.credit_card_debt -= paid
            s.monthly_emi -= paid / 24
        elif s.personal_loan > 0:
            paid = min(s.personal_loan, payment)
            s.personal_loan -= paid
            s.monthly_emi -= paid / 36
        elif s.home_loan > 0:
            paid = min(s.home_loan, payment)
            s.home_loan -= paid
            s.monthly_emi -= paid / 120
        s.monthly_emi = max(0.0, s.monthly_emi)

    elif action == "increase_sip":
        increase = surplus * 0.2
        s.monthly_sip += increase

    elif action == "reduce_discretionary_expenses":
        cut = expenses * 0.10
        s.monthly_expenses = max(expenses * 0.5, expenses - cut)

    elif action == "rebalance_allocation":
        if state.risk_appetite in ("moderate", "aggressive"):
            shift = s.debt_portfolio * 0.10
            s.debt_portfolio -= shift
            s.equity_portfolio += shift
            s.expected_return += 0.3

    elif action == "delay_retirement":
        s.retirement_age = min(s.retirement_age + 2, 70)

    return s


def _extract_metrics(state: FinancialState) -> Dict[str, float]:
    return {
        "success_prob": state.real_success_probability,
        "ef_months": state.emergency_fund_months,
        "dti": state.debt_to_income_ratio,
        "car": state.corpus_adequacy_ratio,
        "stress": state.financial_stress_score,
    }


def _normalize(values: List[float]) -> List[float]:
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.5] * len(values)
    return [(value - lo) / (hi - lo) for value in values]


class PriorityEngine:
    def rank_actions(self, state: FinancialState, top_n: int = 6) -> List[Dict]:
        profile = state.risk_appetite.lower()
        weights = WEIGHT_PROFILES.get(profile, WEIGHT_PROFILES["moderate"])

        baseline = _extract_metrics(state)
        results = []

        for action in ACTIONS:
            new_state = _simulate_action(state, action)
            new_metrics = _extract_metrics(new_state)

            delta_sp = new_metrics["success_prob"] - baseline["success_prob"]
            delta_ef = new_metrics["ef_months"] - baseline["ef_months"]
            delta_dti = baseline["dti"] - new_metrics["dti"]
            delta_car = new_metrics["car"] - baseline["car"]
            delta_str = baseline["stress"] - new_metrics["stress"]

            results.append(
                {
                    "action": action,
                    "deltas": [delta_sp, delta_ef, delta_dti, delta_car, delta_str],
                    "new_metrics": new_metrics,
                }
            )

        normed = [[] for _ in results]
        for dim_idx in range(5):
            dim_values = [result["deltas"][dim_idx] for result in results]
            normalized = _normalize(dim_values)
            for idx, value in enumerate(normalized):
                normed[idx].append(value)

        ranked = []
        for idx, result in enumerate(results):
            score = sum(weight * value for weight, value in zip(weights, normed[idx]))
            score += _action_context_bonus(state, result["action"])
            ranked.append(
                {
                    "rank": 0,
                    "action": result["action"],
                    "composite_score": round(score, 4),
                    "impact": {
                        "success_probability_delta": round(result["deltas"][0], 4),
                        "emergency_fund_months_delta": round(result["deltas"][1], 4),
                        "dti_reduction": round(result["deltas"][2], 4),
                        "corpus_adequacy_delta": round(result["deltas"][3], 4),
                        "stress_reduction": round(result["deltas"][4], 4),
                    },
                    "projected_metrics": {
                        key: round(value, 4)
                        for key, value in result["new_metrics"].items()
                    },
                    "rationale": _rationale(result["action"]),
                }
            )

        ranked.sort(key=lambda item: item["composite_score"], reverse=True)
        for idx, result in enumerate(ranked):
            result["rank"] = idx + 1

        return ranked[:top_n]


def _rationale(action: str) -> str:
    descriptions = {
        "build_emergency_fund": "Builds financial cushion to absorb shocks without debt.",
        "clear_high_interest_debt": "Eliminates high-cost debt, improving cash flow and stress.",
        "increase_sip": "Boosts long-term corpus through compounding.",
        "reduce_discretionary_expenses": "Increases surplus available for goals.",
        "rebalance_allocation": "Optimizes risk-return by shifting to higher-return assets.",
        "delay_retirement": "Extends accumulation window, significantly improving corpus.",
    }
    return descriptions.get(action, "")
