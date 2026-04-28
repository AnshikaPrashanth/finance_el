from typing import List, Dict, Any
from app.models.schemas import UserProfile, Metrics, Explainability, RecommendationItem

def generate_explainability(profile: UserProfile, metrics: Metrics) -> Explainability:
    
    # Goal Analysis
    if metrics.corpus_adequacy_ratio < 0.8:
        goal_analysis = f"Target corpus shortfall. Real projected corpus is only {metrics.corpus_adequacy_ratio*100:.0f}% of the goal due to inflation drag ({metrics.inflation_assumption:.1f}% assumed)."
    elif metrics.success_probability_real < 0.7:
        goal_analysis = "You are on track nominally, but market volatility and inflation pose a risk. Real success probability is below optimal thresholds."
    else:
        goal_analysis = "Your current plan is highly robust. You have a high probability of reaching your inflation-adjusted target corpus."

    # Debt Analysis
    high_interest_debt = profile.liabilities.personal_loan + profile.liabilities.credit_card_debt
    if high_interest_debt > 0:
        debt_analysis = "You carry unsecured/high-interest debt. Prioritize clearing this before aggressively investing, as the interest drag is severe."
    elif metrics.debt_to_income_ratio > 0.4:
        debt_analysis = f"EMI payments consume {metrics.debt_to_income_ratio*100:.0f}% of your monthly income, reducing investable surplus and increasing fragility."
    else:
        debt_analysis = "Your debt levels appear manageable and do not overly constrain your cash flow."

    # Liquidity Analysis
    if metrics.emergency_fund_months < 3:
        liquidity_analysis = f"Emergency reserves are critically low (covers {metrics.emergency_fund_months:.1f} months of essential expenses). Aim for at least 3-6 months."
    elif metrics.emergency_fund_months < 6:
        liquidity_analysis = "Emergency fund is adequate but could be stronger for major shocks."
    else:
        liquidity_analysis = "You have excellent liquidity and a strong emergency buffer."

    return Explainability(
        goal_analysis=goal_analysis,
        debt_analysis=debt_analysis,
        liquidity_analysis=liquidity_analysis
    )

def generate_recommendations(profile: UserProfile, metrics: Metrics, scenarios: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Generate structured recommendations based on profile and metrics.
    
    Args:
        profile: User's financial profile
        metrics: Calculated financial metrics
        scenarios: Optional list of scenario data
    
    Returns:
        List of recommendation objects with details
    """
    recs = []
    
    # High-interest debt priority
    high_interest_debt = profile.liabilities.personal_loan + profile.liabilities.credit_card_debt
    if high_interest_debt > 0:
        debt_months = high_interest_debt / metrics.monthly_surplus if metrics.monthly_surplus > 0 else 999
        recs.append({
            "title": "Clear High-Interest Debt",
            "description": f"You have ₹{high_interest_debt:,.0f} in high-interest debt. Focus on clearing this first as the interest rate (15-20%+) significantly exceeds investment returns.",
            "impact": "high",
            "category": "debt",
            "action": f"Pay off in {min(debt_months, 36):.0f} months with dedicated monthly payments"
        })
        
    # Emergency fund recommendations
    if metrics.emergency_fund_months < 3:
        req_fund = profile.expenses.essential_expenses * 6
        current_fund = profile.assets.savings + profile.assets.emergency_fund
        shortfall = max(0, req_fund - current_fund)
        recs.append({
            "title": "Build Critical Emergency Fund",
            "description": f"Your emergency fund (₹{current_fund:,.0f}) covers only {metrics.emergency_fund_months:.1f} months. Critical situations need 3-6 months of expenses.",
            "impact": "high",
            "category": "liquidity",
            "action": f"Save ₹{shortfall:,.0f} to reach 6-month target"
        })
    elif metrics.emergency_fund_months < 6:
        req_fund = profile.expenses.essential_expenses * 6
        current_fund = profile.assets.savings + profile.assets.emergency_fund
        shortfall = max(0, req_fund - current_fund)
        recs.append({
            "title": "Strengthen Emergency Reserve",
            "description": "Your emergency fund is moderate. Building it to 6 months provides protection against major shocks.",
            "impact": "medium",
            "category": "liquidity",
            "action": f"Allocate ₹{shortfall:,.0f} to reach 6-month coverage"
        })
        
    # Corpus adequacy
    if metrics.corpus_adequacy_ratio < 1.0:
        sip_10 = next((s for s in (scenarios or []) if "SIP +10%" in s.name), None)
        if sip_10 and profile.investments.sip_amount > 0:
            improvement = sip_10.projected_real_corpus - metrics.projected_real_corpus
            recs.append({
                "title": "Increase Monthly SIP Investment",
                "description": f"Increasing SIP by 10% improves your real corpus by ₹{improvement:,.0f} (from ₹{metrics.projected_real_corpus:,.0f} to ₹{sip_10.projected_real_corpus:,.0f}).",
                "impact": "high",
                "category": "investment",
                "action": f"Increase SIP from ₹{profile.investments.sip_amount:,.0f} to ₹{profile.investments.sip_amount * 1.1:,.0f}"
            })
        else:
            if profile.investments.sip_amount > 0:
                recs.append({
                    "title": "Boost Investment Commitment",
                    "description": f"To close the real corpus gap ({metrics.corpus_adequacy_ratio*100:.0f}%), consider increasing SIP by 10-20%.",
                    "impact": "high",
                    "category": "investment",
                    "action": f"Increase SIP from ₹{profile.investments.sip_amount:,.0f} to ₹{profile.investments.sip_amount * 1.15:,.0f}"
                })
            else:
                recs.append({
                    "title": "Start Systematic Investment Plan",
                    "description": "No monthly SIP is set. Starting a systematic investment helps compound wealth over time.",
                    "impact": "high",
                    "category": "investment",
                    "action": "Start monthly SIP based on your surplus"
                })
        
    # Expense optimization
    if metrics.expense_ratio > 0.75:
        discretionary = profile.expenses.discretionary_expenses
        recs.append({
            "title": "Optimize Discretionary Spending",
            "description": f"Your expenses consume {metrics.expense_ratio*100:.0f}% of income. Discretionary spending of ₹{discretionary:,.0f}/month has room for optimization.",
            "impact": "medium",
            "category": "liquidity",
            "action": f"Reduce discretionary spending by 10-15% to free up ₹{discretionary * 0.125:,.0f}/month"
        })
    
    # Asset allocation for young investors
    equity_allocation = profile.investments.asset_allocation.get("equity", 60)
    if equity_allocation < 50 and (profile.personal.retirement_age - profile.personal.age) > 10:
        recs.append({
            "title": "Consider Higher Equity Exposure",
            "description": f"With {profile.personal.retirement_age - profile.personal.age} years to retirement, your {equity_allocation}% equity allocation is conservative. More equity could provide higher real returns.",
            "impact": "medium",
            "category": "investment",
            "action": f"Gradually increase equity to 60-70% of portfolio"
        })
    
    # Tax optimization
    if profile.income.monthly_salary > 0:
        nps_contribution = min(profile.income.monthly_salary * 0.10, 2500)  # 80CCD limit
        recs.append({
            "title": "Maximize Tax-Advantaged Investments",
            "description": "Use PPF, NPS, and 80C benefits to reduce taxable income while building retirement corpus.",
            "impact": "medium",
            "category": "taxes",
            "action": f"Maximize NPS contribution up to ₹{nps_contribution:,.0f}/month for tax benefits"
        })
    
    if not recs:
        recs.append({
            "title": "Maintain Current Plan",
            "description": "Your financial plan is well-balanced and disciplined.",
            "impact": "low",
            "category": "investment",
            "action": "Continue with your current strategy"
        })
        
    return recs
