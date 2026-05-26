from typing import Any, Dict, List

from app.models.schemas import Explainability, Metrics, UserProfile


def _scenario_lookup(scenarios: List[Dict[str, Any]] | None) -> Dict[str, Any]:
    return {item.name: item for item in (scenarios or [])}


def _add_recommendation(
    items: List[Dict[str, Any]],
    *,
    key: str,
    title: str,
    description: str,
    impact: str,
    category: str,
    action: str,
    priority: int,
) -> None:
    items.append(
        {
            "key": key,
            "title": title,
            "description": description,
            "impact": impact,
            "category": category,
            "action": action,
            "priority": priority,
        }
    )


def generate_explainability(profile: UserProfile, metrics: Metrics) -> Explainability:
    if metrics.success_probability_real < 0.20:
        goal_analysis = (
            "Your current savings trajectory may fall short of your retirement goal, "
            "but the gap is still improvable. Increasing SIP contributions, extending "
            "the horizon, or slightly raising equity exposure can materially improve outcomes."
        )
    elif metrics.success_probability_real < 0.55:
        goal_analysis = (
            "Your plan has a workable base, though inflation and market variability still "
            "create a meaningful shortfall risk. A few disciplined adjustments can lift "
            "your long-term success odds."
        )
    else:
        goal_analysis = (
            "Your retirement plan is building on a solid foundation. Staying consistent "
            "with contributions and maintaining diversification should keep you on course."
        )

    high_interest_debt = profile.liabilities.personal_loan + profile.liabilities.credit_card_debt
    if high_interest_debt > 0 and metrics.debt_to_income_ratio > 0.18:
        debt_analysis = (
            "High-interest debt is consuming cash flow that could otherwise strengthen your "
            "savings plan. Reducing unsecured balances should improve flexibility quickly."
        )
    elif metrics.debt_to_income_ratio > 0.40:
        debt_analysis = (
            f"EMI payments are taking up about {metrics.debt_to_income_ratio * 100:.0f}% "
            "of monthly income. Managing repayment carefully will improve resilience without "
            "requiring drastic lifestyle changes."
        )
    else:
        debt_analysis = (
            "Your current debt load looks manageable for your income profile. Keeping unsecured "
            "borrowing low will help preserve long-term momentum."
        )

    if metrics.emergency_fund_months < 3:
        liquidity_analysis = (
            f"Your emergency reserve currently covers about {metrics.emergency_fund_months:.1f} "
            "months of essential expenses. Building this toward 6 months will make the plan "
            "feel much sturdier during income or health shocks."
        )
    elif metrics.emergency_fund_months < 6:
        liquidity_analysis = (
            "Your liquidity is developing well. One more push toward a full 6-month emergency "
            "buffer would add meaningful stability."
        )
    else:
        liquidity_analysis = (
            "You have a healthy liquidity cushion that should absorb many routine disruptions "
            "without derailing long-term goals."
        )

    return Explainability(
        goal_analysis=goal_analysis,
        debt_analysis=debt_analysis,
        liquidity_analysis=liquidity_analysis,
    )


def generate_recommendations(
    profile: UserProfile, metrics: Metrics, scenarios: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    recs: List[Dict[str, Any]] = []
    scenario_map = _scenario_lookup(scenarios)

    monthly_income = (
        profile.income.monthly_salary
        + profile.income.side_income
        + profile.income.rental_income
        + profile.income.other_income
        + (profile.income.bonus / 12)
    )
    high_interest_debt = profile.liabilities.personal_loan + profile.liabilities.credit_card_debt
    target_emergency_fund = profile.expenses.essential_expenses * 6
    emergency_shortfall = max(0.0, target_emergency_fund - profile.assets.emergency_fund)
    surplus = max(0.0, metrics.monthly_surplus)
    equity_allocation = profile.investments.asset_allocation.get("equity", 60)
    years_to_retirement = profile.personal.retirement_age - profile.personal.age

    if metrics.emergency_fund_months < 3:
        _add_recommendation(
            recs,
            key="build_emergency_fund",
            title="Build Emergency Buffer First",
            description=(
                "Your plan would feel more resilient with a stronger emergency reserve. "
                "Before stretching for higher returns, focus on protecting the next 3-6 months "
                "of essential expenses."
            ),
            impact="high",
            category="liquidity",
            action=f"Add approximately INR {emergency_shortfall:,.0f} to fully fund your 6-month emergency reserve",
            priority=100,
        )
    elif metrics.emergency_fund_months < 6:
        _add_recommendation(
            recs,
            key="strengthen_emergency_buffer",
            title="Strengthen Emergency Reserve",
            description=(
                "You already have a useful cash cushion. Topping it up to 6 months would make "
                "job or medical shocks much easier to absorb."
            ),
            impact="medium",
            category="liquidity",
            action=f"Add approximately INR {emergency_shortfall:,.0f} to fully fund your 6-month emergency reserve",
            priority=78,
        )

    if high_interest_debt > 0 and (
        profile.liabilities.credit_card_debt > 0
        or metrics.debt_to_income_ratio > 0.18
        or metrics.monthly_surplus < profile.expenses.emi_payments * 1.2
    ):
        payoff_months = high_interest_debt / max(surplus, 1.0)
        _add_recommendation(
            recs,
            key="clear_high_interest_debt",
            title="Reduce High-Interest Debt",
            description=(
                "A moderate amount of unsecured debt is manageable, but clearing the costliest "
                "balances will free up cash flow faster than chasing small return improvements."
            ),
            impact="high" if profile.liabilities.credit_card_debt > 0 else "medium",
            category="debt",
            action=f"Channel surplus to clear INR {high_interest_debt:,.0f} over about {min(payoff_months, 36):.0f} months",
            priority=92 if profile.liabilities.credit_card_debt > 0 else 74,
        )

    if profile.investments.sip_amount <= 0:
        suggested_sip = max(1000.0, min(surplus * 0.25, monthly_income * 0.10))
        _add_recommendation(
            recs,
            key="start_sip",
            title="Start a Monthly SIP",
            description=(
                "A steady SIP is one of the simplest ways to turn surplus into long-term progress. "
                "Even a modest start builds momentum."
            ),
            impact="high",
            category="investment",
            action=f"Start with a SIP of about INR {suggested_sip:,.0f} per month",
            priority=88,
        )
    elif surplus > profile.investments.sip_amount * 0.75 and metrics.success_probability_real < 0.55:
        recommended_sip = min(profile.investments.sip_amount + surplus * 0.20, profile.investments.sip_amount * 1.25)
        _add_recommendation(
            recs,
            key="increase_sip",
            title="Increase Monthly SIP Gradually",
            description=(
                "Your cash flow appears healthy enough to step up investing without making the "
                "plan feel restrictive. A gradual SIP increase can materially improve your "
                "retirement trajectory."
            ),
            impact="high",
            category="investment",
            action=f"Increase SIP from INR {profile.investments.sip_amount:,.0f} to about INR {recommended_sip:,.0f}",
            priority=84,
        )

    if metrics.expense_ratio > 0.72 and profile.expenses.discretionary_expenses > 0:
        trim_amount = profile.expenses.discretionary_expenses * 0.12
        _add_recommendation(
            recs,
            key="optimize_spend",
            title="Trim Discretionary Spending",
            description=(
                "Your budget is carrying a fairly high expense load. A small cut in optional "
                "spending could improve both emergency savings and investment capacity."
            ),
            impact="medium",
            category="liquidity",
            action=f"Reduce discretionary spend by around INR {trim_amount:,.0f} per month",
            priority=70,
        )

    if metrics.success_probability_real < 0.20 and years_to_retirement <= 15:
        _add_recommendation(
            recs,
            key="delay_retirement",
            title="Consider a Later Retirement Date",
            description=(
                "The current target looks stretched for the remaining time horizon. Extending "
                "the accumulation period by even 2-3 years can meaningfully improve the outcome."
            ),
            impact="high",
            category="planning",
            action=f"Model retirement at age {min(profile.personal.retirement_age + 2, 70)} as a fallback path",
            priority=86,
        )

    if metrics.success_probability_real < 0.35 and equity_allocation < 55 and years_to_retirement >= 12:
        _add_recommendation(
            recs,
            key="rebalance_allocation",
            title="Review Long-Term Asset Allocation",
            description=(
                "Your horizon is long enough to consider a slightly higher equity allocation, "
                "which may improve real return potential without requiring a dramatic change."
            ),
            impact="medium",
            category="investment",
            action="Gradually move toward 60-70% equity if it suits your risk comfort",
            priority=73,
        )

    if profile.expenses.insurance <= 0:
        _add_recommendation(
            recs,
            key="add_insurance",
            title="Review Insurance Protection",
            description=(
                "Insurance does not directly grow wealth, but it protects the plan you are building. "
                "A basic health and term cover review can reduce the impact of major shocks."
            ),
            impact="medium",
            category="protection",
            action="Review health and term insurance adequacy for your family needs",
            priority=68,
        )

    if monthly_income > 0:
        nps_contribution = min(profile.income.monthly_salary * 0.10, 2500)
        _add_recommendation(
            recs,
            key="tax_optimization",
            title="Use Tax-Efficient Retirement Buckets",
            description=(
                "Tax-saving instruments like NPS, PPF, and EPF can improve after-tax wealth "
                "creation while keeping the plan disciplined."
            ),
            impact="medium",
            category="taxes",
            action=f"Consider an NPS contribution up to INR {nps_contribution:,.0f} per month",
            priority=54,
        )

    if not recs:
        _add_recommendation(
            recs,
            key="maintain_plan",
            title="Stay Consistent With the Current Plan",
            description=(
                "Your finances appear balanced overall. Staying disciplined with contributions "
                "and periodic reviews should keep the plan on a healthy path."
            ),
            impact="low",
            category="investment",
            action="Continue your current savings and review the plan every 6-12 months",
            priority=40,
        )

    # Use scenario outcomes to lift the most relevant growth lever when the retirement
    # shortfall is large, instead of repeating the same debt recommendation every time.
    if metrics.success_probability_real < 0.40 and scenario_map:
        retire_later = scenario_map.get("Retire Later")
        debt_first = scenario_map.get("Clear High-Interest Debt")
        sip_twenty = scenario_map.get("SIP +20%")
        best_growth = max(
            [item for item in [retire_later, debt_first, sip_twenty] if item is not None],
            key=lambda item: item.success_probability,
            default=None,
        )
        if best_growth:
            _add_recommendation(
                recs,
                key="best_scenario_lever",
                title="Prioritize the Most Effective Improvement Lever",
                description=(
                    f"Among the modeled scenarios, '{best_growth.name}' produced the strongest "
                    "improvement in retirement readiness. This is a practical place to focus next."
                ),
                impact="medium",
                category="planning",
                action=best_growth.summary,
                priority=67,
            )

    recs.sort(key=lambda item: item["priority"], reverse=True)

    seen_keys = set()
    final_items = []
    for item in recs:
        if item["key"] in seen_keys:
            continue
        seen_keys.add(item["key"])
        final_items.append(
            {
                "title": item["title"],
                "description": item["description"],
                "impact": item["impact"],
                "category": item["category"],
                "action": item["action"],
            }
        )
        if len(final_items) >= 5:
            break

    return final_items
