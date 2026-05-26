from app.models.schemas import UserProfile, Metrics
from app.services.assumptions_service import (
    calculate_portfolio_metrics,
    get_inflation_assumption,
    get_income_growth_assumption,
)
from app.services.tax_engine import calculate_estimated_taxes


HEALTH_SCORE_WEIGHTS = {
    "savings": 0.20,
    "emergency_fund": 0.18,
    "debt_burden": 0.15,
    "sip_consistency": 0.12,
    "insurance_readiness": 0.08,
    "liquidity": 0.10,
    "diversification": 0.07,
    "goal_progress": 0.10,
}


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _blend_linear(value: float, anchors: list[tuple[float, float]]) -> float:
    if not anchors:
        return 0.0
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


def _savings_score(savings_rate: float) -> float:
    return _blend_linear(
        savings_rate,
        [
            (0.00, 5),
            (0.05, 22),
            (0.10, 42),
            (0.20, 68),
            (0.30, 88),
            (0.40, 100),
        ],
    )


def _emergency_fund_score(months: float) -> float:
    return _blend_linear(
        months,
        [
            (0.0, 0),
            (1.0, 20),
            (3.0, 50),
            (4.0, 64),
            (6.0, 84),
            (9.0, 100),
        ],
    )


def _debt_burden_score(debt_to_income_ratio: float, high_interest_ratio: float) -> float:
    base = _blend_linear(
        debt_to_income_ratio,
        [
            (0.00, 96),
            (0.10, 90),
            (0.20, 78),
            (0.30, 62),
            (0.40, 48),
            (0.55, 28),
            (0.75, 10),
        ],
    )
    penalty = _blend_linear(
        high_interest_ratio,
        [
            (0.00, 0),
            (0.05, 4),
            (0.10, 9),
            (0.20, 16),
            (0.35, 24),
        ],
    )
    return _clamp((base - penalty) / 100, 0.0, 1.0) * 100


def _sip_score(monthly_sip: float, monthly_income: float) -> float:
    if monthly_income <= 0:
        return 0.0
    sip_ratio = monthly_sip / monthly_income
    if monthly_sip <= 0:
        return 6.0
    return _blend_linear(
        sip_ratio,
        [
            (0.00, 40),
            (0.03, 56),
            (0.06, 72),
            (0.10, 88),
            (0.15, 100),
        ],
    )


def _insurance_score(insurance_premium_ratio: float) -> float:
    # The data model does not include coverage amount, so recurring insurance spend
    # is used as a proxy for baseline protection instead of exact adequacy.
    if insurance_premium_ratio <= 0:
        return 28.0
    return _blend_linear(
        insurance_premium_ratio,
        [
            (0.00, 52),
            (0.01, 62),
            (0.03, 76),
            (0.05, 88),
            (0.08, 100),
        ],
    )


def _liquidity_score(liquid_months: float) -> float:
    return _blend_linear(
        liquid_months,
        [
            (0.0, 8),
            (1.0, 24),
            (3.0, 48),
            (6.0, 72),
            (9.0, 88),
            (12.0, 100),
        ],
    )


def _diversification_score(profile: UserProfile, total_assets: float) -> float:
    asset_buckets = {
        "cash": profile.assets.savings + profile.assets.emergency_fund,
        "fixed_income": profile.assets.fixed_deposits + profile.assets.nps,
        "equity": profile.assets.stocks + profile.assets.mutual_funds,
        "retirement": profile.assets.epf + profile.assets.ppf,
        "real_assets": profile.assets.gold + profile.assets.real_estate,
        "other": profile.assets.business_assets + profile.assets.other_assets,
    }
    active_buckets = sum(1 for value in asset_buckets.values() if value > 0)
    base = _blend_linear(
        active_buckets,
        [
            (1, 20),
            (2, 40),
            (3, 58),
            (4, 74),
            (5, 88),
            (6, 100),
        ],
    )

    if total_assets <= 0:
        return base

    largest_bucket_ratio = max(asset_buckets.values()) / total_assets
    concentration_penalty = _blend_linear(
        largest_bucket_ratio,
        [
            (0.35, 0),
            (0.50, 4),
            (0.65, 10),
            (0.80, 18),
            (0.95, 28),
        ],
    )
    return max(0.0, base - concentration_penalty)


def _goal_progress_score(corpus_adequacy_ratio: float) -> float:
    return _blend_linear(
        corpus_adequacy_ratio,
        [
            (0.00, 10),
            (0.25, 26),
            (0.50, 46),
            (0.75, 64),
            (1.00, 82),
            (1.30, 100),
        ],
    )


def _calculate_financial_health_score(
    profile: UserProfile,
    monthly_income: float,
    total_assets: float,
    savings_rate: float,
    emergency_fund_months: float,
    debt_to_income_ratio: float,
    corpus_adequacy_ratio: float,
) -> float:
    essential_expenses = max(profile.expenses.essential_expenses, 1.0)
    liquid_assets = (
        profile.assets.savings + profile.assets.emergency_fund + profile.assets.fixed_deposits
    )
    liquid_months = liquid_assets / essential_expenses
    high_interest_ratio = (
        profile.liabilities.high_interest_debt / (monthly_income * 12)
        if monthly_income > 0
        else 1.0
    )
    insurance_premium_ratio = (
        profile.expenses.insurance / monthly_income if monthly_income > 0 else 0.0
    )

    factor_scores = {
        "savings": _savings_score(savings_rate),
        "emergency_fund": _emergency_fund_score(emergency_fund_months),
        "debt_burden": _debt_burden_score(debt_to_income_ratio, high_interest_ratio),
        "sip_consistency": _sip_score(profile.investments.sip_amount, monthly_income),
        "insurance_readiness": _insurance_score(insurance_premium_ratio),
        "liquidity": _liquidity_score(liquid_months),
        "diversification": _diversification_score(profile, total_assets),
        "goal_progress": _goal_progress_score(corpus_adequacy_ratio),
    }

    weighted_score = sum(
        factor_scores[key] * HEALTH_SCORE_WEIGHTS[key] for key in HEALTH_SCORE_WEIGHTS
    )
    return round(_clamp(weighted_score / 100, 0.0, 1.0) * 100, 4)


def calculate_metrics(profile: UserProfile) -> Metrics:
    assets = profile.assets
    liabilities = profile.liabilities
    income = profile.income
    expenses = profile.expenses
    investments = profile.investments

    total_assets = sum(
        [
            assets.savings,
            assets.emergency_fund,
            assets.fixed_deposits,
            assets.stocks,
            assets.mutual_funds,
            assets.epf,
            assets.ppf,
            assets.nps,
            assets.gold,
            assets.real_estate,
            assets.business_assets,
            assets.other_assets,
        ]
    )

    total_liabilities = sum(
        [
            liabilities.home_loan,
            liabilities.personal_loan,
            liabilities.vehicle_loan,
            liabilities.education_loan,
            liabilities.credit_card_debt,
            liabilities.other_liabilities,
        ]
    )

    net_worth = total_assets - total_liabilities

    monthly_income = sum(
        [
            income.monthly_salary,
            income.bonus / 12,
            income.side_income,
            income.rental_income,
            income.other_income,
        ]
    )

    monthly_essential_expenses = expenses.essential_expenses
    monthly_total_expenses = monthly_essential_expenses + expenses.discretionary_expenses

    annual_income = monthly_income * 12
    annual_tax = calculate_estimated_taxes(annual_income, mode="current")
    monthly_tax = annual_tax / 12

    monthly_surplus = monthly_income - monthly_total_expenses - monthly_tax
    savings_rate = monthly_surplus / monthly_income if monthly_income > 0 else 0
    expense_ratio = monthly_total_expenses / monthly_income if monthly_income > 0 else 0
    debt_to_income_ratio = (
        expenses.emi_payments / monthly_income if monthly_income > 0 else 0
    )

    emergency_fund_months = (
        assets.emergency_fund / monthly_essential_expenses
        if monthly_essential_expenses > 0
        else 0
    )

    target_corpus = investments.target_corpus
    if target_corpus <= 0:
        target_corpus = monthly_total_expenses * 12 * 25

    exp_return, vol = calculate_portfolio_metrics(investments.asset_allocation)
    inflation = get_inflation_assumption(profile)
    income_growth = get_income_growth_assumption()

    years_to_retire = profile.personal.retirement_age - profile.personal.age
    r = exp_return
    monthly_r = r / 12
    n = years_to_retire * 12

    future_assets_nominal = total_assets * ((1 + r) ** years_to_retire)
    if monthly_r > 0:
        sip_future_nominal = (
            investments.sip_amount
            * (((1 + monthly_r) ** n - 1) / monthly_r)
            * (1 + monthly_r)
        )
    else:
        sip_future_nominal = investments.sip_amount * n

    projected_corpus_nominal = future_assets_nominal + sip_future_nominal
    projected_corpus_real = projected_corpus_nominal / ((1 + inflation) ** years_to_retire)
    corpus_adequacy_ratio = (
        projected_corpus_real / target_corpus if target_corpus > 0 else 1.0
    )

    success_probability_nominal = min(
        projected_corpus_nominal / target_corpus if target_corpus > 0 else 1.0,
        1.0,
    )
    success_probability_real = min(
        projected_corpus_real / target_corpus if target_corpus > 0 else 1.0,
        1.0,
    )

    financial_health_score = _calculate_financial_health_score(
        profile=profile,
        monthly_income=monthly_income,
        total_assets=total_assets,
        savings_rate=savings_rate,
        emergency_fund_months=emergency_fund_months,
        debt_to_income_ratio=debt_to_income_ratio,
        corpus_adequacy_ratio=corpus_adequacy_ratio,
    )

    return Metrics(
        net_worth=round(net_worth, 4),
        total_assets=round(total_assets, 4),
        total_liabilities=round(total_liabilities, 4),
        monthly_surplus=round(monthly_surplus, 4),
        savings_rate=round(savings_rate, 4),
        financial_health_score=financial_health_score,
        target_corpus=round(target_corpus, 4),
        projected_corpus=round(projected_corpus_nominal, 4),
        projected_real_corpus=round(projected_corpus_real, 4),
        success_probability=round(success_probability_nominal, 4),
        success_probability_nominal=round(success_probability_nominal, 4),
        success_probability_real=round(success_probability_real, 4),
        shortfall_probability=round(1.0 - success_probability_real, 4),
        corpus_adequacy_ratio=round(corpus_adequacy_ratio, 4),
        emergency_fund_months=round(emergency_fund_months, 4),
        debt_to_income_ratio=round(debt_to_income_ratio, 4),
        expense_ratio=round(expense_ratio, 4),
        portfolio_expected_return=round(exp_return * 100, 4),
        portfolio_volatility=round(vol * 100, 4),
        inflation_assumption=round(inflation * 100, 4),
        income_growth_assumption=round(income_growth * 100, 4),
    )
