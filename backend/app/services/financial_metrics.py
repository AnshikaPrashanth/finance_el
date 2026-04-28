from app.models.schemas import UserProfile, Metrics
from app.services.assumptions_service import calculate_portfolio_metrics, get_inflation_assumption, get_income_growth_assumption
from app.services.tax_engine import calculate_estimated_taxes

def calculate_metrics(profile: UserProfile) -> Metrics:
    assets = profile.assets
    liabilities = profile.liabilities
    income = profile.income
    expenses = profile.expenses
    investments = profile.investments

    total_assets = sum([
        assets.savings, assets.emergency_fund, assets.fixed_deposits,
        assets.stocks, assets.mutual_funds, assets.epf, assets.ppf,
        assets.nps, assets.gold, assets.real_estate,
        assets.business_assets, assets.other_assets
    ])

    total_liabilities = sum([
        liabilities.home_loan, liabilities.personal_loan, liabilities.vehicle_loan,
        liabilities.education_loan, liabilities.credit_card_debt, liabilities.other_liabilities
    ])

    net_worth = total_assets - total_liabilities

    monthly_income = sum([
        income.monthly_salary, income.bonus / 12, income.side_income,
        income.rental_income, income.other_income
    ])

    monthly_essential_expenses = expenses.essential_expenses
    monthly_total_expenses = monthly_essential_expenses + expenses.discretionary_expenses
    
    annual_income = monthly_income * 12
    annual_tax = calculate_estimated_taxes(annual_income, mode="current")
    monthly_tax = annual_tax / 12

    monthly_surplus = monthly_income - monthly_total_expenses - monthly_tax
    savings_rate = monthly_surplus / monthly_income if monthly_income > 0 else 0
    expense_ratio = monthly_total_expenses / monthly_income if monthly_income > 0 else 0
    
    monthly_emi = liabilities.home_loan * 0.01 + liabilities.personal_loan * 0.02 + liabilities.vehicle_loan * 0.015 # Simplified proxy if EMI not given
    # But we have expenses.emi_payments in the schema:
    monthly_emi_actual = expenses.emi_payments
    debt_to_income_ratio = monthly_emi_actual / monthly_income if monthly_income > 0 else 0

    emergency_fund_months = assets.emergency_fund / monthly_essential_expenses if monthly_essential_expenses > 0 else 0

    # Target Corpus: 25x annual total expenses if not provided
    target_corpus = investments.target_corpus
    if target_corpus <= 0:
        target_corpus = monthly_total_expenses * 12 * 25

    # Portfolio math
    exp_return, vol = calculate_portfolio_metrics(investments.asset_allocation)
    inflation = get_inflation_assumption(profile)
    income_growth = get_income_growth_assumption()
    
    # Future Value calculations
    years_to_retire = profile.personal.retirement_age - profile.personal.age
    
    r = exp_return
    monthly_r = r / 12
    n = years_to_retire * 12
    
    # FV of Lumpsum (assets)
    future_assets_nominal = total_assets * ((1 + r) ** years_to_retire)
    
    # FV of SIP
    if monthly_r > 0:
        sip_future_nominal = investments.sip_amount * (((1 + monthly_r) ** n - 1) / monthly_r) * (1 + monthly_r)
    else:
        sip_future_nominal = investments.sip_amount * n
        
    projected_corpus_nominal = future_assets_nominal + sip_future_nominal
    
    # Real corpus
    projected_corpus_real = projected_corpus_nominal / ((1 + inflation) ** years_to_retire)

    corpus_adequacy_ratio = projected_corpus_real / target_corpus if target_corpus > 0 else 1.0

    # Simple deterministic success prob approximation (real Monte Carlo overrides this later)
    success_probability_nominal = min(projected_corpus_nominal / target_corpus if target_corpus > 0 else 1.0, 1.0)
    success_probability_real = min(projected_corpus_real / target_corpus if target_corpus > 0 else 1.0, 1.0)

    # Health Score weighting
    hs = 0
    if savings_rate >= 0.20: hs += 25 * min(savings_rate / 0.30, 1.0)
    if emergency_fund_months >= 3: hs += 25 * min(emergency_fund_months / 6, 1.0)
    if debt_to_income_ratio <= 0.40: hs += 25 * (1 - (debt_to_income_ratio / 0.40))
    hs += 25 * min(corpus_adequacy_ratio, 1.0)
    
    financial_health_score = max(0, min(100, hs))

    return Metrics(
        net_worth=round(net_worth, 4),
        total_assets=round(total_assets, 4),
        total_liabilities=round(total_liabilities, 4),
        monthly_surplus=round(monthly_surplus, 4),
        savings_rate=round(savings_rate, 4),
        financial_health_score=round(financial_health_score, 4),
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
        income_growth_assumption=round(income_growth * 100, 4)
    )
