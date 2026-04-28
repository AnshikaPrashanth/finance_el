import numpy as np
from typing import List, Tuple, Dict, Any
import datetime
from app.models.schemas import UserProfile, MonteCarloPoint, Metrics
from app.services.assumptions_service import calculate_portfolio_metrics, get_inflation_assumption, get_income_growth_assumption
from app.services.tax_engine import calculate_estimated_taxes

def run_monte_carlo(profile: UserProfile, metrics: Metrics, num_simulations: int = 1000) -> Tuple[List[MonteCarloPoint], float, float, Dict[str, Any]]:
    years = profile.personal.retirement_age - profile.personal.age
    if years <= 0:
        return [], 1.0, 0.0, {}

    initial_portfolio = metrics.total_assets
    
    mean_return, volatility = calculate_portfolio_metrics(profile.investments.asset_allocation)
    mean_inflation = get_inflation_assumption(profile)
    mean_income_growth = get_income_growth_assumption()
    
    inflation_volatility = 0.02
    income_growth_volatility = 0.015
    
    current_year = datetime.datetime.now().year
    
    results = []
    
    final_real_wealths = np.zeros(num_simulations)
    
    wealths = np.full(num_simulations, initial_portfolio)
    cumulative_inflation_factors = np.ones(num_simulations)
    cumulative_income_growth = np.ones(num_simulations)
    
    # Base values for realistic step-by-step scaling
    base_annual_income = (
        profile.income.monthly_salary + profile.income.bonus / 12 + 
        profile.income.side_income + profile.income.rental_income + 
        profile.income.other_income
    ) * 12
    
    base_annual_expenses = (profile.expenses.essential_expenses + profile.expenses.discretionary_expenses) * 12
    base_annual_debt = (
        profile.liabilities.home_loan * 0.01 + 
        profile.liabilities.personal_loan * 0.02 + 
        profile.liabilities.vehicle_loan * 0.015
    ) * 12 # proxy for debt if EMI is zero, otherwise:
    if profile.expenses.emi_payments > 0:
        base_annual_debt = profile.expenses.emi_payments * 12

    # Debug trace recording (we record the median path for debug purposes)
    debug_trace = {
        "yearly_projections": [],
        "initial_portfolio": initial_portfolio,
        "mean_return_assumed": mean_return,
        "volatility_assumed": volatility
    }
    
    for year in range(1, years + 1):
        sampled_returns = np.random.normal(mean_return, volatility, num_simulations)
        sampled_inflations = np.random.normal(mean_inflation, inflation_volatility, num_simulations)
        sampled_income_growth = np.random.normal(mean_income_growth, income_growth_volatility, num_simulations)
        
        cumulative_inflation_factors *= (1 + sampled_inflations)
        cumulative_income_growth *= (1 + sampled_income_growth)
        
        # Calculate year-specific cash flows for each simulation
        annual_incomes = base_annual_income * cumulative_income_growth
        annual_expenses = base_annual_expenses * cumulative_inflation_factors
        # Debt payments stay flat (not indexed to inflation)
        annual_debts = np.full(num_simulations, base_annual_debt)
        
        # Simple vectorized tax calculation
        # To avoid slow python loops, we approximate tax drag as 15% across the board in MC
        annual_taxes = annual_incomes * 0.15 
        
        annual_surpluses = annual_incomes - annual_expenses - annual_debts - annual_taxes
        
        # Ensure surplus isn't negative (can't invest negative, just 0)
        annual_investments = np.maximum(annual_surpluses, 0)
        
        # Override with strict SIP constraint if the user wants strict SIP logic:
        # However, for rigorous step-by-step, investable surplus is realistic.
        # We will bound the investment to at least the user's intended SIP, scaled by inflation
        intended_sips = profile.investments.sip_amount * 12 * cumulative_inflation_factors
        
        # We use intended SIPs unless surplus completely dries up
        actual_additions = np.minimum(annual_investments, intended_sips) if base_annual_income > 0 else intended_sips
        
        # Grow wealth
        wealths = wealths * (1 + sampled_returns) + actual_additions
        
        real_wealths = wealths / cumulative_inflation_factors
        
        # Calculate percentiles
        p5 = float(np.percentile(wealths, 5))
        p50 = float(np.percentile(wealths, 50))
        p95 = float(np.percentile(wealths, 95))
        
        p5_real = float(np.percentile(real_wealths, 5))
        p50_real = float(np.percentile(real_wealths, 50))
        p95_real = float(np.percentile(real_wealths, 95))
        
        results.append(MonteCarloPoint(
            year=current_year + year,
            p5=p5,
            p50=p50,
            p95=p95,
            p5_real=p5_real,
            p50_real=p50_real,
            p95_real=p95_real
        ))
        
        # Record debug trace for the median path
        debug_trace["yearly_projections"].append({
            "year": current_year + year,
            "median_nominal_wealth": p50,
            "median_real_wealth": p50_real,
            "median_income_grown": float(np.median(annual_incomes)),
            "median_expenses_grown": float(np.median(annual_expenses)),
            "median_invested": float(np.median(actual_additions))
        })
        
        if year == years:
            final_real_wealths = real_wealths
            
    # Calculate success probability
    target = metrics.target_corpus
    successful_runs = np.sum(final_real_wealths >= target)
    success_prob_real = float(successful_runs / num_simulations) if num_simulations > 0 else 0.0
    shortfall_prob = 1.0 - success_prob_real
    
    debug_trace["final_real_p5"] = float(np.percentile(final_real_wealths, 5)) if len(final_real_wealths) > 0 else 0
    debug_trace["final_real_p50"] = float(np.percentile(final_real_wealths, 50)) if len(final_real_wealths) > 0 else 0
    debug_trace["final_real_p95"] = float(np.percentile(final_real_wealths, 95)) if len(final_real_wealths) > 0 else 0
    
    return results, success_prob_real, shortfall_prob, debug_trace
