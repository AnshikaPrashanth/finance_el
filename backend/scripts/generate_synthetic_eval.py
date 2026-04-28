import os
import sys
import csv
import random

# Add parent dir to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.schemas import UserProfile, PersonalInfo, IncomeInfo, ExpenseInfo, AssetInfo, LiabilityInfo, InvestmentGoals
from app.services.simulation_engine import run_simulation

def generate_synthetic_profile(profile_id: int) -> UserProfile:
    age = random.randint(25, 50)
    retirement_age = random.randint(55, 65)
    if retirement_age <= age:
        retirement_age = age + 10
        
    monthly_salary = random.randint(50000, 300000)
    essential_expenses = monthly_salary * random.uniform(0.3, 0.6)
    discretionary_expenses = monthly_salary * random.uniform(0.1, 0.3)
    
    savings = random.randint(100000, 1000000)
    stocks = random.randint(0, 5000000)
    
    personal_loan = random.randint(0, 500000) if random.random() > 0.5 else 0
    
    sip_amount = monthly_salary * random.uniform(0.05, 0.3)
    equity_alloc = random.choice([40, 60, 80])
    
    return UserProfile(
        personal=PersonalInfo(name=f"Synth_{profile_id}", age=age, retirement_age=retirement_age, city="Test", marital_status="Single", dependents=0),
        income=IncomeInfo(monthly_salary=monthly_salary),
        expenses=ExpenseInfo(living_expenses=essential_expenses, discretionary_spending=discretionary_expenses),
        assets=AssetInfo(savings=savings, stocks=stocks, emergency_fund=savings*0.5),
        liabilities=LiabilityInfo(personal_loan=personal_loan),
        investments=InvestmentGoals(
            sip_amount=sip_amount, 
            expected_annual_return=12.0, 
            inflation_rate=6.0, 
            target_corpus=0, # Auto-calc
            asset_allocation={"equity": equity_alloc, "debt": 100 - equity_alloc}
        )
    )

def main():
    print("Generating synthetic profiles and running evaluations...")
    results = []
    
    for i in range(1, 21): # 20 profiles
        profile = generate_synthetic_profile(i)
        sim_result = run_simulation(profile)
        
        base_scenario = next(s for s in sim_result.scenarios if s.name == "Base")
        best_scenario = max(sim_result.scenarios, key=lambda s: s.success_probability)
        
        results.append({
            "Profile ID": i,
            "Age": profile.personal.age,
            "Income": profile.income.monthly_salary,
            "SIP": profile.investments.sip_amount,
            "Equity %": profile.investments.asset_allocation["equity"],
            "Target Real Corpus": sim_result.metrics.target_corpus,
            "Base Success Prob": f"{base_scenario.success_probability*100:.1f}%",
            "Best Scenario": best_scenario.name,
            "Best Success Prob": f"{best_scenario.success_probability*100:.1f}%",
            "Base Real Corpus": f"{base_scenario.projected_real_corpus:,.0f}",
            "Best Real Corpus": f"{best_scenario.projected_real_corpus:,.0f}"
        })
        
    # Write to CSV
    csv_file = "evaluation_results.csv"
    with open(csv_file, 'w', newline='') as csvfile:
        fieldnames = results[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
            
    print(f"Evaluation complete. Results saved to {csv_file}")

if __name__ == "__main__":
    main()
