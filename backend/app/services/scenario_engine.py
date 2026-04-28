from typing import List, Dict, Any
from app.models.schemas import UserProfile, ScenarioPoint
from app.services.financial_metrics import calculate_metrics
from app.services.monte_carlo import run_monte_carlo

def generate_scenarios(profile: UserProfile, base_prob_real: float = None) -> List[ScenarioPoint]:
    scenarios = []
    
    def run_scenario(name: str, p: UserProfile, summary: str, changed_inputs: Dict[str, Any], base_corpus: float = 0.0) -> ScenarioPoint:
        m = calculate_metrics(p)
        
        if name == "Base" and base_prob_real is not None:
            prob_real = base_prob_real
        else:
            # To keep it fast, we do 500 trials for scenarios instead of 1000
            _, prob_real, _, _ = run_monte_carlo(p, m, num_simulations=500)
        
        change_vs_base = m.projected_real_corpus - base_corpus if base_corpus > 0 else 0.0
        
        return ScenarioPoint(
            name=name,
            projected_corpus=m.projected_corpus,
            projected_real_corpus=m.projected_real_corpus,
            success_probability=prob_real, # use real stochastic probability
            corpus_adequacy_ratio=m.corpus_adequacy_ratio,
            change_vs_base=change_vs_base,
            summary=summary,
            changed_inputs=changed_inputs,
            path=[] # Add deterministic path if needed, but omitted for payload size
        )

    def clone_profile() -> UserProfile:
        return UserProfile.model_validate(profile.model_dump())

    # 1. Base
    base_p = clone_profile()
    base_scenario = run_scenario(
        "Base", base_p,
        "Current plan based on existing assumptions.",
        {}, 0.0
    )
    scenarios.append(base_scenario)
    base_corpus = base_scenario.projected_real_corpus
    
    # 2. SIP +10%
    p_sip_10 = clone_profile()
    p_sip_10.investments.sip_amount *= 1.10
    scenarios.append(run_scenario(
        "SIP +10%", p_sip_10,
        "Increasing monthly investments accelerates wealth accumulation.",
        {"sip_amount": f"+10% (now {p_sip_10.investments.sip_amount})"},
        base_corpus
    ))

    # 3. SIP +20%
    p_sip_20 = clone_profile()
    p_sip_20.investments.sip_amount *= 1.20
    scenarios.append(run_scenario(
        "SIP +20%", p_sip_20,
        "Aggressive increase in investments significantly boosts probability.",
        {"sip_amount": f"+20% (now {p_sip_20.investments.sip_amount})"},
        base_corpus
    ))

    # 4. Reduce expenses
    p_exp = clone_profile()
    original_disc = p_exp.expenses.discretionary_spending
    saved = original_disc * 0.2
    p_exp.expenses.discretionary_spending *= 0.8
    p_exp.investments.sip_amount += saved
    scenarios.append(run_scenario(
        "Reduce Expenses", p_exp,
        "Cutting discretionary spend by 20% and diverting it to SIP.",
        {
            "discretionary_spending": f"-20% (now {p_exp.expenses.discretionary_spending})",
            "sip_amount": f"+{saved} (now {p_exp.investments.sip_amount})"
        },
        base_corpus
    ))

    # 5. Retire later
    p_retire = clone_profile()
    p_retire.personal.retirement_age += 2
    scenarios.append(run_scenario(
        "Retire Later", p_retire,
        "Working 2 more years allows compound interest more time to work.",
        {"retirement_age": f"+2 years (now {p_retire.personal.retirement_age})"},
        base_corpus
    ))

    # 6. Debt-prepayment-first
    p_debt = clone_profile()
    # Simulate paying off high-interest debt using liquid assets/surplus
    high_interest_debt = p_debt.liabilities.personal_loan + p_debt.liabilities.credit_card_debt
    if high_interest_debt > 0:
        p_debt.liabilities.personal_loan = 0
        p_debt.liabilities.credit_card_debt = 0
        p_debt.assets.savings = max(0, p_debt.assets.savings - high_interest_debt)
        # Removing EMIs frees up SIP
        p_debt.investments.sip_amount += p_debt.expenses.emi_payments * 0.5 # assuming half EMI was for these loans
        p_debt.expenses.emi_payments *= 0.5
        scenarios.append(run_scenario(
            "Clear High-Interest Debt", p_debt,
            "Clearing unsecured debt reduces financial fragility and frees up cash flow.",
            {
                "personal_loan": "0",
                "credit_card_debt": "0",
                "savings": "Reduced to pay debt",
                "sip_amount": "Increased by freed EMI"
            },
            base_corpus
        ))

    return scenarios
