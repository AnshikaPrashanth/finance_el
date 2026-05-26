"""
state_engine.py - Adaptive Personal Financial Decision Twin
===========================================================
Represents the user's financial state as a structured, mutable vector.
Implements state cloning, derived metric computation, and history logging.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Dict, List
import copy
import math


@dataclass
class FinancialState:
    """
    Core financial state vector. Monetary values in INR unless noted.
    Derived metrics are computed properties - not stored fields.
    """

    user_id: str = "default"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    # Income & Expenses (monthly)
    monthly_income: float = 100_000.0
    monthly_expenses: float = 60_000.0
    monthly_sip: float = 10_000.0
    monthly_emi: float = 15_000.0

    # Assets (total INR)
    liquid_savings: float = 200_000.0
    equity_portfolio: float = 500_000.0
    debt_portfolio: float = 100_000.0
    real_estate: float = 0.0
    epf_ppf: float = 300_000.0
    emergency_fund: float = 150_000.0
    monthly_insurance_premium: float = 0.0

    # Liabilities (outstanding principal, INR)
    home_loan: float = 2_000_000.0
    personal_loan: float = 100_000.0
    credit_card_debt: float = 20_000.0
    home_loan_rate: float = 8.5
    personal_loan_rate: float = 14.0
    credit_card_rate: float = 36.0

    # Goals & Preferences
    target_corpus: float = 50_000_000.0
    current_age: int = 35
    retirement_age: int = 60
    dependents: int = 2
    risk_appetite: str = "moderate"

    # Market Assumptions
    expected_return: float = 10.0
    inflation_rate: float = 6.0

    # Simulation flags
    is_employed: bool = True
    months_of_job_loss: int = 0

    @property
    def real_return(self) -> float:
        return round(
            (
                (1 + self.expected_return / 100)
                / (1 + self.inflation_rate / 100)
                - 1
            )
            * 100,
            4,
        )

    @property
    def monthly_surplus(self) -> float:
        if not self.is_employed:
            return 0.0
        return max(
            0.0,
            self.monthly_income
            - self.monthly_expenses
            - self.monthly_sip
            - self.monthly_emi,
        )

    @property
    def total_assets(self) -> float:
        return (
            self.liquid_savings
            + self.equity_portfolio
            + self.debt_portfolio
            + self.real_estate
            + self.epf_ppf
            + self.emergency_fund
        )

    @property
    def total_liabilities(self) -> float:
        return self.home_loan + self.personal_loan + self.credit_card_debt

    @property
    def net_worth(self) -> float:
        return self.total_assets - self.total_liabilities

    @property
    def debt_to_income_ratio(self) -> float:
        return (
            round(self.monthly_emi / self.monthly_income, 4)
            if self.monthly_income
            else float("inf")
        )

    @property
    def emergency_fund_months(self) -> float:
        return (
            round(self.emergency_fund / self.monthly_expenses, 2)
            if self.monthly_expenses
            else 0.0
        )

    @property
    def years_to_retirement(self) -> int:
        return max(0, self.retirement_age - self.current_age)

    @property
    def projected_corpus(self) -> float:
        r = self.real_return / 100 / 12
        n = self.years_to_retirement * 12
        if n == 0:
            return self.total_assets

        pv = self.equity_portfolio + self.debt_portfolio + self.epf_ppf
        fv_lump = pv * ((1 + r) ** n)
        fv_sip = (
            self.monthly_sip * (((1 + r) ** n - 1) / r) * (1 + r)
            if r > 0
            else self.monthly_sip * n
        )
        return round(fv_lump + fv_sip, 2)

    @property
    def corpus_adequacy_ratio(self) -> float:
        return (
            round(self.projected_corpus / self.target_corpus, 4)
            if self.target_corpus
            else 1.0
        )

    @property
    def financial_stress_score(self) -> float:
        dti_pressure = min(1.0, self.debt_to_income_ratio / 0.55)
        ef_gap = max(0.0, 1.0 - self.emergency_fund_months / 6.0)
        goal_gap = max(0.0, 1.0 - min(self.corpus_adequacy_ratio, 1.2) / 1.2)
        surplus_gap = 1.0 - min(
            1.0,
            self.monthly_surplus / max(self.monthly_income * 0.15, 1.0),
        )
        employment_risk = 0.0 if self.is_employed else 1.0
        return round(
            0.22 * dti_pressure
            + 0.24 * ef_gap
            + 0.24 * goal_gap
            + 0.18 * surplus_gap
            + 0.12 * employment_risk,
            4,
        )

    @property
    def real_success_probability(self) -> float:
        car = self.corpus_adequacy_ratio
        liquidity_boost = min(
            0.12,
            (
                (self.liquid_savings + self.emergency_fund) / max(self.monthly_expenses * 6, 1.0)
            )
            * 0.12,
        )
        sip_boost = min(0.08, self.monthly_sip / max(self.monthly_income * 0.15, 1.0) * 0.08)
        insurance_boost = 0.04 if self.monthly_insurance_premium > 0 else 0.0
        logit = 3.6 * (car - 0.78)
        prob = 1 / (1 + math.exp(-logit))
        return round(
            max(
                0.0,
                min(
                    1.0,
                    prob * (1 - 0.18 * self.financial_stress_score)
                    + liquidity_boost
                    + sip_boost
                    + insurance_boost,
                ),
            ),
            4,
        )

    def to_dict(self) -> Dict:
        base = asdict(self)
        base.update(
            {
                "real_return": self.real_return,
                "monthly_surplus": self.monthly_surplus,
                "total_assets": self.total_assets,
                "total_liabilities": self.total_liabilities,
                "net_worth": self.net_worth,
                "debt_to_income_ratio": self.debt_to_income_ratio,
                "emergency_fund_months": self.emergency_fund_months,
                "years_to_retirement": self.years_to_retirement,
                "projected_corpus": self.projected_corpus,
                "corpus_adequacy_ratio": self.corpus_adequacy_ratio,
                "financial_stress_score": self.financial_stress_score,
                "real_success_probability": self.real_success_probability,
            }
        )
        return base

    def clone(self) -> "FinancialState":
        return copy.deepcopy(self)


class StateHistory:
    def __init__(self) -> None:
        self.snapshots: List[Dict] = []
        self.events: List[str] = []

    def record(self, state: FinancialState, label: str = "baseline") -> None:
        self.snapshots.append(state.to_dict())
        self.events.append(label)

    def diff(self, idx_a: int = -2, idx_b: int = -1) -> Dict:
        if len(self.snapshots) < 2:
            return {}
        a, b = self.snapshots[idx_a], self.snapshots[idx_b]
        return {
            key: round(b[key] - a[key], 4)
            for key in b
            if isinstance(b[key], (int, float)) and key in a
        }

    def to_dict(self) -> Dict[str, List]:
        return {"snapshots": self.snapshots, "events": self.events}
