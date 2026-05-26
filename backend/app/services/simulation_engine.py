import uuid
import datetime
from app.models.schemas import UserProfile, SimulationResult, ProjectionPoint, CashFlowPoint, AssumptionVersions
from app.services.financial_metrics import calculate_metrics
from app.services.monte_carlo import run_monte_carlo
from app.services.scenario_engine import generate_scenarios
from app.services.explainability import generate_explainability, generate_recommendations
from app.services.market_data_service import get_market_assumptions_version
from app.services.tax_engine import get_tax_version

def run_simulation(profile: UserProfile) -> SimulationResult:
    sim_id = str(uuid.uuid4())
    
    # Base deterministic metrics
    metrics = calculate_metrics(profile)
    
    # Stochastic Monte Carlo
    monte_carlo, success_prob_real, shortfall_prob, debug_trace = run_monte_carlo(profile, metrics, num_simulations=1000)
    
    # Unify success probability metrics using stochastic outcome
    metrics.success_probability_real = success_prob_real
    metrics.success_probability_nominal = success_prob_real
    metrics.success_probability = success_prob_real
    
    # Scenarios (each does its own deterministic + monte carlo internally)
    scenarios = generate_scenarios(profile, base_prob_real=success_prob_real)
    
    # Text generation based on rigorous metrics
    explainability = generate_explainability(profile, metrics)
    recommendations = generate_recommendations(profile, metrics, scenarios)
    
    # Base deterministic net worth projection
    nw_proj = []
    current_year = datetime.datetime.now().year
    current_nw = metrics.net_worth
    annual_savings = metrics.monthly_surplus * 12
    r = metrics.portfolio_expected_return / 100
    inf = metrics.inflation_assumption / 100
    
    cumulative_inflation = 1.0
    
    for i in range(11):
        real_nw = current_nw / cumulative_inflation
        nw_proj.append(ProjectionPoint(year=current_year + i, value=current_nw, real_value=real_nw))
        current_nw = current_nw * (1 + r) + annual_savings
        cumulative_inflation *= (1 + inf)
        
    total_income_annual = sum([
        profile.income.monthly_salary, profile.income.bonus/12, 
        profile.income.side_income, profile.income.rental_income, 
        profile.income.other_income
    ]) * 12
    
    total_expenses_annual = (profile.expenses.essential_expenses + profile.expenses.discretionary_expenses) * 12
    
    cf = [
        CashFlowPoint(
            period=str(current_year),
            income=total_income_annual,
            expenses=total_expenses_annual,
            surplus=total_income_annual - total_expenses_annual
        )
    ]

    # Version tracking
    assumptions = AssumptionVersions(
        tax_version=get_tax_version(),
        market_version=get_market_assumptions_version(),
        inflation_assumption=metrics.inflation_assumption,
        income_growth_assumption=metrics.income_growth_assumption
    )

    result = SimulationResult(
        simulation_id=sim_id,
        status="completed",
        user_summary={
            "name": profile.personal.name,
            "age": profile.personal.age,
            "retirement_age": profile.personal.retirement_age
        },
        metrics=metrics,
        net_worth_projection=nw_proj,
        cash_flow=cf,
        monte_carlo=monte_carlo,
        scenarios=scenarios,
        recommendations=recommendations,
        explainability=explainability,
        assumptions=assumptions,
        debug_info={
            **(debug_trace or {}),
            "generated_at": datetime.datetime.utcnow().isoformat()
        }
    )
    
    return result
